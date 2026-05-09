from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import render

from .like_annotations import annotate_viewer_question_likes


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    raw = request.GET.get("page", 1)
    try:
        page_number = int(raw)
    except (TypeError, ValueError):
        return paginator.page(1)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        raise Http404("Страницы с таким номером не существует.")


def render_paginated_question_list(
    request,
    queryset,
    *,
    template: str,
    page_title: str,
    list_title: str,
    per_page: int = 5,
    extra_context=None,
):
    queryset = annotate_viewer_question_likes(queryset, request.user)
    ctx = {
        "page_title": page_title,
        "list_title": list_title,
        "page": paginate(queryset, request, per_page=per_page),
    }
    if extra_context:
        ctx.update(extra_context)
    return render(request, template, ctx)
