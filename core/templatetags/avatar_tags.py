from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def user_avatar_src(user):
    if user is None or not getattr(user, "pk", None):
        return static("core/img/avatar-placeholder.svg")
    try:
        if user.profile.avatar:
            return user.profile.avatar.url
    except ObjectDoesNotExist:
        pass
    return static("core/img/avatar-placeholder.svg")
