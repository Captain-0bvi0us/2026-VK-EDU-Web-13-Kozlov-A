from django.shortcuts import get_object_or_404, redirect, render

from .models import Answer, Question, Tag
from .presentation import render_paginated_question_list
from .utils import paginate


def index(request):
    return render_paginated_question_list(
        request,
        Question.objects.new(),
        template="questions/index.html",
        page_title="Новые вопросы — CupOfQ",
        list_title="Новые вопросы",
        nav_variant="user",
        per_page=5,
    )


def hot(request):
    return render_paginated_question_list(
        request,
        Question.objects.popular(),
        template="questions/hot.html",
        page_title="Горячие вопросы — CupOfQ",
        list_title="Горячие вопросы",
        nav_variant="user",
        per_page=5,
    )


def tag(request, tag):
    tag_obj = get_object_or_404(Tag, slug=tag)
    return render_paginated_question_list(
        request,
        Question.objects.for_tag_slug(tag_obj.slug),
        template="questions/tag.html",
        page_title=f"Тег: {tag_obj.name} — CupOfQ",
        list_title="",
        nav_variant="user",
        per_page=5,
        extra_context={"tag_name": tag_obj.name},
    )


def question_detail(request, pk):
    if request.method == "POST":
        return redirect("question_detail", pk=pk)
    question = get_object_or_404(Question.objects.with_list_defaults(), pk=pk)
    page = paginate(Answer.objects.for_question(question), request, per_page=3)
    return render(
        request,
        "questions/question.html",
        {
            "page_title": f"{question.title} — CupOfQ",
            "question": question,
            "page": page,
            "nav_variant": "guest",
        },
    )


def ask(request):
    if request.method == "POST":
        return redirect("ask")
    return render(
        request,
        "questions/ask.html",
        {"page_title": "Новый вопрос — CupOfQ", "nav_variant": "user"},
    )
