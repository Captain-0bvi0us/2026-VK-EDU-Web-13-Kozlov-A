from django.shortcuts import redirect, render

from .dummy import build_answers, build_questions
from .utils import paginate


def index(request):
    questions = build_questions(30)
    page = paginate(questions, request, per_page=5)
    return render(
        request,
        "questions/index.html",
        {
            "page_title": "Новые вопросы — CupOfQ",
            "list_title": "Новые вопросы",
            "page": page,
            "nav_variant": "user",
        },
    )


def hot(request):
    questions = build_questions(25)
    page = paginate(questions, request, per_page=5)
    return render(
        request,
        "questions/hot.html",
        {
            "page_title": "Горячие вопросы — CupOfQ",
            "list_title": "Горячие вопросы",
            "page": page,
            "nav_variant": "user",
        },
    )


def tag(request, tag):
    questions = build_questions(20)
    page = paginate(questions, request, per_page=5)
    return render(
        request,
        "questions/tag.html",
        {
            "page_title": f"Тег: {tag} — CupOfQ",
            "tag_name": tag,
            "page": page,
            "nav_variant": "user",
        },
    )


def question_detail(request, pk):
    if request.method == "POST":
        return redirect("question_detail", pk=pk)
    answers = build_answers(pk, 22)
    page = paginate(answers, request, per_page=3)
    return render(
        request,
        "questions/question.html",
        {
            "page_title": f"Вопрос #{pk} — CupOfQ",
            "question": {
                "id": pk,
                "title": "Как построить лунный парк?",
                "text": "Lorem ipsum dolor sit amet — текст вопроса-заглушки для ДЗ2.",
                "created": "3 марта 2026, 14:20",
                "author": "Гость",
                "score": 5,
                "tags": [
                    {"name": "блэкджек", "slug": "blackjack"},
                    {"name": "bender", "slug": "bender"},
                ],
            },
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
        {
            "page_title": "Новый вопрос — CupOfQ",
            "nav_variant": "user",
        },
    )
