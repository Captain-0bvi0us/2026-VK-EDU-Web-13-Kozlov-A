import random
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag, VoteSign

User = get_user_model()
BATCH = 4000


class Command(BaseCommand):
    help = (
        "Наполняет БД тестовыми данными: users=ratio, questions=ratio*10, "
        "answers=ratio*100, tags=ratio, суммарно лайков (вопрос+ответ)=ratio*200. "
        "Рассчитано на PostgreSQL; лучше запускать на новой/пустой схеме."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "ratio",
            type=int,
            help="Коэффициент: столько будет создано пользователей (и остальное по формулам).",
        )

    def handle(self, *args, **options):
        ratio = options["ratio"]
        if ratio < 1:
            raise CommandError("ratio должно быть >= 1")

        fake = Faker("ru_RU")
        fake.unique.clear()
        rng = random.Random(42)

        n_tags = ratio
        n_users = ratio
        n_questions = ratio * 10
        n_answers = ratio * 100
        n_likes_total = ratio * 200
        n_q_likes = n_likes_total // 2
        n_a_likes = n_likes_total - n_q_likes

        if n_users * n_questions < n_q_likes:
            raise CommandError(
                f"При ratio={ratio} нельзя добавить {n_q_likes} уникальных лайков вопросов "
                f"(лимит {n_users}×{n_questions}={n_users * n_questions}). Укажите ratio ≥ 10."
            )
        if n_users * n_answers < n_a_likes:
            raise CommandError(
                f"При ratio={ratio} нельзя добавить {n_a_likes} уникальных лайков ответов "
                f"(лимит {n_users * n_answers}). Увеличьте ratio."
            )

        self.stdout.write(
            f"План: теги={n_tags}, пользователи={n_users}, вопросы={n_questions}, "
            f"ответы={n_answers}, лайки вопросов={n_q_likes}, лайков ответов={n_a_likes}"
        )

        run_id = uuid.uuid4().hex[:8]
        pwd_hash = make_password("filldb")

        tag_pks = self._fill_tags(fake, run_id, n_tags)
        user_pks = self._fill_users(fake, run_id, pwd_hash, n_users)
        self._fill_profiles(user_pks)
        question_pks = self._fill_questions(fake, rng, user_pks, n_questions)
        self._fill_question_tags(rng, question_pks, tag_pks)
        answer_pks = self._fill_answers(fake, rng, user_pks, question_pks, n_answers)

        self._bulk_unique_likes(
            QuestionLike,
            n_q_likes,
            user_pks,
            question_pks,
            lambda u, q: QuestionLike(
                user_id=u,
                question_id=q,
                value=VoteSign.UP if rng.random() < 0.55 else VoteSign.DOWN,
            ),
        )
        self._bulk_unique_likes(
            AnswerLike,
            n_a_likes,
            user_pks,
            answer_pks,
            lambda u, a: AnswerLike(
                user_id=u,
                answer_id=a,
                value=VoteSign.UP if rng.random() < 0.55 else VoteSign.DOWN,
            ),
        )

        self.stdout.write(self.style.SUCCESS("Готово."))

    def _random_dt(self, rng: random.Random, *, max_days: int) -> timezone.datetime:
        return timezone.now() - timedelta(
            days=rng.randint(0, max(0, max_days - 1)),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )

    def _fill_tags(self, fake: Faker, run_id: str, n_tags: int) -> list[int]:
        tag_pks = []
        for i in range(0, n_tags, BATCH):
            chunk = [
                Tag(
                    name=(fake.word().capitalize()[:50] + f"-{run_id}-{j}")[:64],
                    slug=f"t-{run_id}-{j}-{uuid.uuid4().hex[:8]}"[:64],
                )
                for j in range(i, min(i + BATCH, n_tags))
            ]
            with transaction.atomic():
                Tag.objects.bulk_create(chunk, batch_size=BATCH)
            tag_pks.extend(t.pk for t in chunk)
        return tag_pks

    def _fill_users(
        self, fake: Faker, run_id: str, pwd_hash: str, n_users: int
    ) -> list[int]:
        user_pks = []
        for i in range(0, n_users, BATCH):
            chunk = [
                User(
                    username=f"{run_id}_u{j}",
                    email=f"{run_id}_u{j}@filldb.local",
                    password=pwd_hash,
                    first_name=(fake.first_name()[:150]),
                    last_name=(fake.last_name()[:150]),
                )
                for j in range(i, min(i + BATCH, n_users))
            ]
            with transaction.atomic():
                User.objects.bulk_create(chunk, batch_size=BATCH)
            user_pks.extend(u.pk for u in chunk)
        return user_pks

    def _fill_profiles(self, user_pks: list[int]) -> None:
        profiles = [Profile(user_id=uid) for uid in user_pks]
        for i in range(0, len(profiles), BATCH):
            with transaction.atomic():
                Profile.objects.bulk_create(
                    profiles[i : i + BATCH], batch_size=BATCH, ignore_conflicts=True
                )

    def _fill_questions(
        self,
        fake: Faker,
        rng: random.Random,
        user_pks: list[int],
        n_questions: int,
    ) -> list[int]:
        question_pks = []
        for i in range(0, n_questions, BATCH):
            chunk = [
                Question(
                    author_id=rng.choice(user_pks),
                    title=fake.sentence(nb_words=6)[:250],
                    text="\n\n".join(fake.paragraphs(nb=3)),
                    created_at=self._random_dt(rng, max_days=90),
                )
                for _ in range(min(BATCH, n_questions - i))
            ]
            with transaction.atomic():
                Question.objects.bulk_create(chunk, batch_size=BATCH)
            question_pks.extend(q.pk for q in chunk)
        return question_pks

    def _fill_question_tags(
        self,
        rng: random.Random,
        question_pks: list[int],
        tag_pks: list[int],
    ) -> None:
        Through = Question.tags.through
        through_rows = []
        for qpk in question_pks:
            k = rng.randint(1, min(3, len(tag_pks)))
            for tpk in rng.sample(tag_pks, k):
                through_rows.append(Through(question_id=qpk, tag_id=tpk))
        for i in range(0, len(through_rows), BATCH):
            with transaction.atomic():
                Through.objects.bulk_create(
                    through_rows[i : i + BATCH], batch_size=BATCH, ignore_conflicts=True
                )

    def _fill_answers(
        self,
        fake: Faker,
        rng: random.Random,
        user_pks: list[int],
        question_pks: list[int],
        n_answers: int,
    ) -> list[int]:
        answer_pks = []
        for i in range(0, n_answers, BATCH):
            chunk = [
                Answer(
                    question_id=rng.choice(question_pks),
                    author_id=rng.choice(user_pks),
                    text=fake.text(max_nb_chars=1500),
                    is_correct=False,
                    created_at=self._random_dt(rng, max_days=7),
                )
                for _ in range(min(BATCH, n_answers - i))
            ]
            with transaction.atomic():
                Answer.objects.bulk_create(chunk, batch_size=BATCH)
            answer_pks.extend(a.pk for a in chunk)
        return answer_pks

    def _bulk_unique_likes(self, model, target, user_pks, entity_pks, row_fn):
        if target <= 0 or not user_pks or not entity_pks:
            return
        nu, ne = len(user_pks), len(entity_pks)
        max_pairs = nu * ne
        if target > max_pairs:
            self.stdout.write(
                self.style.WARNING(
                    f"{model.__name__}: запрошено {target} пар, максимум {max_pairs} — создаём {max_pairs}."
                )
            )
            target = max_pairs
        batch = []
        count = 0
        rng = random.Random(42)
        for u in user_pks:
            for e in entity_pks:
                if count >= target:
                    break
                like = row_fn(u, e)
                like.created_at = self._random_dt(rng, max_days=7)
                batch.append(like)
                count += 1
                if len(batch) >= BATCH:
                    with transaction.atomic():
                        model.objects.bulk_create(batch, batch_size=BATCH)
                    batch.clear()
            if count >= target:
                break
        if batch:
            with transaction.atomic():
                model.objects.bulk_create(batch, batch_size=BATCH)
