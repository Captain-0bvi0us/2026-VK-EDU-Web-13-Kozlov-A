from django.db.models import BooleanField, Exists, OuterRef, Value

from .models import AnswerLike, QuestionLike


def annotate_viewer_question_likes(queryset, user):
    if user.is_authenticated:
        return queryset.annotate(
            viewer_has_like=Exists(
                QuestionLike.objects.filter(
                    question_id=OuterRef("pk"),
                    user_id=user.pk,
                )
            )
        )
    return queryset.annotate(
        viewer_has_like=Value(False, output_field=BooleanField())
    )


def annotate_viewer_answer_likes(queryset, user):
    if user.is_authenticated:
        return queryset.annotate(
            viewer_has_like=Exists(
                AnswerLike.objects.filter(
                    answer_id=OuterRef("pk"),
                    user_id=user.pk,
                )
            )
        )
    return queryset.annotate(
        viewer_has_like=Value(False, output_field=BooleanField())
    )
