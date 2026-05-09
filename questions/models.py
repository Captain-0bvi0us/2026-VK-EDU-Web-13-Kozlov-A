from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import formats, timezone


class Tag(models.Model):
    name = models.CharField("название", max_length=64)
    slug = models.SlugField("слаг", max_length=64, unique=True, db_index=True)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("tag", kwargs={"tag": self.slug})


class QuestionQuerySet(models.QuerySet):
    def with_list_defaults(self):
        return (
            self.select_related("author")
            .prefetch_related("tags")
            .annotate(
                score=Count("question_likes", distinct=True),
                answer_count=Count("answers", distinct=True),
            )
        )

    def new(self):
        return self.with_list_defaults().order_by("-created_at")

    def popular(self):
        return self.with_list_defaults().order_by("-score", "-created_at")

    def for_tag_slug(self, slug: str):
        return (
            self.with_list_defaults()
            .filter(tags__slug=slug)
            .distinct()
            .order_by("-created_at")
        )


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def with_list_defaults(self):
        return self.get_queryset().with_list_defaults()

    def new(self):
        return self.get_queryset().new()

    def popular(self):
        return self.get_queryset().popular()

    def for_tag_slug(self, slug: str):
        return self.get_queryset().for_tag_slug(slug)


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="автор",
    )
    title = models.CharField("заголовок", max_length=255)
    text = models.TextField("текст")
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    tags = models.ManyToManyField(
        Tag,
        related_name="questions",
        blank=True,
        verbose_name="теги",
    )

    objects = QuestionManager()

    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("question_detail", kwargs={"pk": self.pk})

    @property
    def created_display(self) -> str:
        dt = timezone.localtime(self.created_at)
        return formats.date_format(dt, "j E Y, H:i")

    @property
    def author_display(self) -> str:
        return self.author.get_username()

    @property
    def vote_state(self) -> str:
        return "none"


class AnswerQuerySet(models.QuerySet):
    def for_question(self, question: "Question"):
        return (
            self.filter(question=question)
            .select_related("author")
            .annotate(score=Count("answer_likes", distinct=True))
            .order_by("-is_correct", "created_at")
        )


class AnswerManager(models.Manager.from_queryset(AnswerQuerySet)):
    pass


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="вопрос",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="автор",
    )
    text = models.TextField("текст")
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    is_correct = models.BooleanField("верный ответ", default=False)

    objects = AnswerManager()

    class Meta:
        verbose_name = "ответ"
        verbose_name_plural = "ответы"
        ordering = ["-is_correct", "created_at"]

    def __str__(self) -> str:
        return f"Ответ к «{self.question.title}»"

    @property
    def created_display(self) -> str:
        dt = timezone.localtime(self.created_at)
        return formats.date_format(dt, "j E Y, H:i")

    @property
    def author_display(self) -> str:
        return self.author.get_username()

    @property
    def vote_state(self) -> str:
        return "none"


class QuestionLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="пользователь",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="вопрос",
    )
    created_at = models.DateTimeField("дата", auto_now_add=True)

    class Meta:
        verbose_name = "лайк вопроса"
        verbose_name_plural = "лайки вопросов"
        unique_together = [["user", "question"]]

    def __str__(self) -> str:
        return f"{self.user} → {self.question_id}"


class AnswerLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="пользователь",
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="ответ",
    )
    created_at = models.DateTimeField("дата", auto_now_add=True)

    class Meta:
        verbose_name = "лайк ответа"
        verbose_name_plural = "лайки ответов"
        unique_together = [["user", "answer"]]

    def __str__(self) -> str:
        return f"{self.user} → ответ {self.answer_id}"
