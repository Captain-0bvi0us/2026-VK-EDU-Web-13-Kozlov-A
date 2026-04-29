from django.shortcuts import render

from .utils import paginate


def render_paginated_question_list(
    request,
    queryset,
    *,
    template: str,
    page_title: str,
    list_title: str,
    nav_variant: str,
    per_page: int = 5,
    extra_context=None,
):
    ctx = {
        "page_title": page_title,
        "list_title": list_title,
        "nav_variant": nav_variant,
        "page": paginate(queryset, request, per_page=per_page),
    }
    if extra_context:
        ctx.update(extra_context)
    return render(request, template, ctx)
