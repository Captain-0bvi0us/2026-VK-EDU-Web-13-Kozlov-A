from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.auth_utils import get_safe_redirect_url

from .forms import AnswerForm, QuestionForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .like_annotations import annotate_viewer_answer_likes, annotate_viewer_question_likes
from .presentation import paginate, render_paginated_question_list


def _page_index_for_answer(answer_qs, answer_pk: int, per_page: int) -> int:
    ids = list(answer_qs.values_list("pk", flat=True))
    try:
        idx = ids.index(answer_pk)
    except ValueError:
        return 1
    return idx // per_page + 1


def index(request):
    return render_paginated_question_list(
        request,
        Question.objects.new(),
        template="questions/index.html",
        page_title="Новые вопросы — CupOfQ",
        list_title="Новые вопросы",
        per_page=5,
    )


def hot(request):
    return render_paginated_question_list(
        request,
        Question.objects.popular(),
        template="questions/hot.html",
        page_title="Горячие вопросы — CupOfQ",
        list_title="Горячие вопросы",
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
        per_page=5,
        extra_context={"tag_name": tag_obj.name},
    )


def question_detail(request, pk):
    qs = annotate_viewer_question_likes(
        Question.objects.with_list_defaults(),
        request.user,
    )
    question = get_object_or_404(qs, pk=pk)
    answer_qs = annotate_viewer_answer_likes(
        Answer.objects.for_question(question),
        request.user,
    )
    per_page = 3
    form = None

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(), login_url="/login/", redirect_field_name="next"
            )
        form = AnswerForm(
            request.POST,
            author=request.user,
            question=question,
        )
        if form.is_valid():
            answer = form.save()
            page_num = _page_index_for_answer(
                answer_qs, answer.pk, per_page=per_page
            )
            url = (
                f"{question.get_absolute_url()}?page={page_num}#answer-{answer.pk}"
            )
            return redirect(url)
    elif request.user.is_authenticated:
        form = AnswerForm(author=request.user, question=question)

    page = paginate(answer_qs, request, per_page=per_page)
    return render(
        request,
        "questions/question.html",
        {
            "page_title": f"{question.title} — CupOfQ",
            "question": question,
            "page": page,
            "answer_form": form,
        },
    )


@login_required
@require_POST
def question_vote(request, pk):
    question = get_object_or_404(Question, pk=pk)
    fallback = question.get_absolute_url()
    next_url = get_safe_redirect_url(
        request,
        request.POST.get("next"),
        fallback=fallback,
    )
    if question.author_id == request.user.id:
        return redirect(next_url)
    action = request.POST.get("action")
    if action == "up":
        QuestionLike.objects.get_or_create(user=request.user, question=question)
    elif action == "down":
        QuestionLike.objects.filter(user=request.user, question=question).delete()
    return redirect(next_url)


@login_required
@require_POST
def answer_vote(request, pk):
    answer = get_object_or_404(Answer.objects.select_related("question"), pk=pk)
    q = answer.question
    fallback = q.get_absolute_url()
    next_url = get_safe_redirect_url(
        request,
        request.POST.get("next"),
        fallback=fallback,
    )
    if answer.author_id == request.user.id:
        return redirect(next_url)
    action = request.POST.get("action")
    if action == "up":
        AnswerLike.objects.get_or_create(user=request.user, answer=answer)
    elif action == "down":
        AnswerLike.objects.filter(user=request.user, answer=answer).delete()
    return redirect(next_url)


@login_required
@require_POST
def mark_answer_correct(request, pk):
    answer = get_object_or_404(Answer.objects.select_related("question"), pk=pk)
    question = answer.question
    fallback = question.get_absolute_url()
    next_url = get_safe_redirect_url(
        request,
        request.POST.get("next"),
        fallback=fallback,
    )
    if question.author_id != request.user.id:
        return redirect(next_url)
    Answer.objects.filter(question=question).update(is_correct=False)
    answer.is_correct = True
    answer.save(update_fields=["is_correct"])
    return redirect(next_url)


@login_required
def ask(request):
    form = QuestionForm(
        request.POST or None,
        author=request.user,
    )
    if request.method == "POST" and form.is_valid():
        q = form.save()
        return redirect(q.get_absolute_url())
    return render(
        request,
        "questions/ask.html",
        {
            "page_title": "Новый вопрос — CupOfQ",
            "form": form,
        },
    )
