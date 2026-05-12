from django.contrib.auth import get_user_model
from django.db.models import Count, F

from questions.models import Tag

User = get_user_model()

POPULAR_TAGS_LIMIT = 8
BEST_MEMBERS_LIMIT = 5

_TAG_SIZES = ("lg", "md", "md", "sm", "sm", "accent", "warm", "sm")


def popular_tags_for_sidebar():
    qs = (
        Tag.objects.annotate(_n=Count("questions", distinct=True))
        .filter(_n__gt=0)
        .order_by("-_n", "name")[:POPULAR_TAGS_LIMIT]
    )
    out = []
    for i, tag in enumerate(qs):
        size = _TAG_SIZES[i] if i < len(_TAG_SIZES) else "sm"
        out.append({"name": tag.name, "slug": tag.slug, "size": size})
    return out


def best_members_for_sidebar():
    qs = (
        User.objects.select_related("profile")
        .annotate(
            _q=Count("questions", distinct=True),
            _a=Count("answers", distinct=True),
        )
        .annotate(activity=F("_q") + F("_a"))
        .filter(activity__gt=0)
        .order_by("-activity", "username")[:BEST_MEMBERS_LIMIT]
    )
    return list(qs)


def sidebar_context(request):
    return {
        "popular_tags": popular_tags_for_sidebar(),
        "best_members": best_members_for_sidebar(),
    }
