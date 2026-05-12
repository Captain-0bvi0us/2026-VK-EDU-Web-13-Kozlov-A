from django.db.models import IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .models import AnswerLike, QuestionLike


def annotate_viewer_question_likes(queryset, user):
    if user.is_authenticated:
        v = QuestionLike.objects.filter(
            question_id=OuterRef("pk"),
            user_id=user.pk,
        ).values("value")[:1]
        return queryset.annotate(
            viewer_vote=Coalesce(
                Subquery(v, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
        )
    return queryset.annotate(
        viewer_vote=Value(0, output_field=IntegerField())
    )


def annotate_viewer_answer_likes(queryset, user):
    if user.is_authenticated:
        v = AnswerLike.objects.filter(
            answer_id=OuterRef("pk"),
            user_id=user.pk,
        ).values("value")[:1]
        return queryset.annotate(
            viewer_vote=Coalesce(
                Subquery(v, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
        )
    return queryset.annotate(
        viewer_vote=Value(0, output_field=IntegerField())
    )
