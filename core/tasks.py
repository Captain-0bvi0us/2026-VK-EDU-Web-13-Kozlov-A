from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Count, F, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from . import cache_keys

logger = logging.getLogger(__name__)

POPULAR_TAGS_LIMIT = 10
POPULAR_TAGS_PERIOD = timedelta(days=90)

BEST_MEMBERS_LIMIT = 10
BEST_MEMBERS_PERIOD = timedelta(days=7)


def _compute_popular_tags() -> list[dict]:
    from questions.models import Tag

    since = timezone.now() - POPULAR_TAGS_PERIOD
    qs = (
        Tag.objects.annotate(
            recent_n=Count("questions", filter=Q(questions__created_at__gte=since))
        )
        .filter(recent_n__gt=0)
        .order_by("-recent_n", "name")[:POPULAR_TAGS_LIMIT]
    )
    return [
        {"name": t.name, "slug": t.slug, "count": t.recent_n}
        for t in qs
    ]


def _compute_best_members() -> list[dict]:
    from questions.models import AnswerLike, QuestionLike

    User = get_user_model()
    since = timezone.now() - BEST_MEMBERS_PERIOD

    q_vote_sum = (
        QuestionLike.objects.filter(
            question__author_id=OuterRef("pk"),
            question__created_at__gte=since,
        )
        .values("question__author_id")
        .annotate(total=Sum("value"))
        .values("total")[:1]
    )
    a_vote_sum = (
        AnswerLike.objects.filter(
            answer__author_id=OuterRef("pk"),
            answer__created_at__gte=since,
        )
        .values("answer__author_id")
        .annotate(total=Sum("value"))
        .values("total")[:1]
    )

    qs = (
        User.objects.select_related("profile")
        .annotate(
            q_score=Coalesce(
                Subquery(q_vote_sum, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            a_score=Coalesce(
                Subquery(a_vote_sum, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        .annotate(score=F("q_score") + F("a_score"))
        .filter(score__gt=0)
        .order_by("-score", "username")[:BEST_MEMBERS_LIMIT]
    )
    out = []
    for u in qs:
        avatar_url = ""
        try:
            if u.profile and u.profile.avatar:
                avatar_url = u.profile.avatar.url
        except Exception:  # noqa: BLE001
            avatar_url = ""
        out.append(
            {
                "username": u.get_username(),
                "display": (u.get_full_name() or u.get_username()),
                "score": int(u.score or 0),
                "avatar_url": avatar_url,
            }
        )
    return out


@shared_task(name="core.tasks.recompute_popular_tags")
def recompute_popular_tags() -> int:
    data = _compute_popular_tags()
    cache.set(cache_keys.POPULAR_TAGS, data, timeout=cache_keys.SIDEBAR_TIMEOUT)
    logger.info("popular_tags recomputed: %d записей", len(data))
    return len(data)


@shared_task(name="core.tasks.recompute_best_members")
def recompute_best_members() -> int:
    data = _compute_best_members()
    cache.set(cache_keys.BEST_MEMBERS, data, timeout=cache_keys.SIDEBAR_TIMEOUT)
    logger.info("best_members recomputed: %d записей", len(data))
    return len(data)


# ---------- Email-уведомления  ----------


@shared_task(name="core.tasks.send_new_answer_email")
def send_new_answer_email(question_id: int, answer_id: int) -> bool:
    """Уведомление автору вопроса о новом ответе."""
    from questions.models import Answer

    try:
        answer = (
            Answer.objects.select_related("question", "question__author", "author")
            .only(
                "id",
                "text",
                "question__id",
                "question__title",
                "question__author__email",
                "question__author__username",
                "author__username",
                "author__first_name",
                "author__last_name",
            )
            .get(pk=answer_id, question_id=question_id)
        )
    except Answer.DoesNotExist:
        logger.warning("send_new_answer_email: ответ %s не найден", answer_id)
        return False

    question = answer.question
    target = question.author
    if not target.email:
        logger.info(
            "send_new_answer_email: у автора %s нет email — пропускаем",
            target.get_username(),
        )
        return False
    if target.id == answer.author_id:
        return False

    subject = f"Новый ответ на ваш вопрос «{question.title}»"
    body = (
        f"Здравствуйте, {target.first_name or target.get_username()}!\n\n"
        f"На ваш вопрос «{question.title}» появился новый ответ "
        f"от {answer.author.get_username()}:\n\n"
        f"{answer.text[:500]}\n\n"
        f"Посмотреть на сайте: /question/{question.pk}/\n"
        "— CupOfQ"
    )
    sent = send_mail(
        subject=subject,
        message=body,
        from_email=None,
        recipient_list=[target.email],
        fail_silently=False,
    )
    return bool(sent)
