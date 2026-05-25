from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .auth_utils import get_safe_logout_redirect, get_safe_redirect_url
from .centrifugo import make_connection_token, question_channel
from .forms import LoginForm, ProfileEditForm, SignupForm
from .models import Profile
from .signup_staging import SESSION_KEY_STAGED_AVATAR, delete_staged, stage_signup_avatar
from .utils import user_display_name

User = get_user_model()


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    next_raw = request.POST.get("next") or request.GET.get("next") or ""
    if request.user.is_authenticated:
        return redirect(get_safe_redirect_url(request, next_raw, fallback="/"))
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(
                get_safe_redirect_url(request, next_raw, fallback="/")
            )
    else:
        form = LoginForm(request)
    return render(
        request,
        "core/login.html",
        {
            "page_title": "Вход — CupOfQ",
            "form": form,
            "next": next_raw,
        },
    )


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "GET":
        delete_staged(request.session.pop(SESSION_KEY_STAGED_AVATAR, None))
        form = SignupForm()
        return render(
            request,
            "core/signup.html",
            {
                "page_title": "Регистрация — CupOfQ",
                "form": form,
                "signup_staged_name": None,
            },
        )
    form = SignupForm(request.POST, request.FILES)
    if form.is_valid():
        staged = request.session.pop(SESSION_KEY_STAGED_AVATAR, None)
        user = form.save(staged_avatar=staged)
        delete_staged(staged)
        login(request, user)
        return redirect("/")
    incoming = request.FILES.get("avatar")
    if incoming and not form.errors.get("avatar"):
        delete_staged(request.session.pop(SESSION_KEY_STAGED_AVATAR, None))
        try:
            request.session[SESSION_KEY_STAGED_AVATAR] = stage_signup_avatar(
                incoming, request.session.session_key or "anon"
            )
        except ValidationError as exc:
            form.add_error("avatar", exc)
    elif incoming and form.errors.get("avatar"):
        delete_staged(request.session.pop(SESSION_KEY_STAGED_AVATAR, None))
    staged = request.session.get(SESSION_KEY_STAGED_AVATAR)
    return render(
        request,
        "core/signup.html",
        {
            "page_title": "Регистрация — CupOfQ",
            "form": form,
            "signup_staged_name": (staged or {}).get("original_name"),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileEditForm(user=request.user)
    display_name = user_display_name(request.user)
    return render(
        request,
        "core/profile.html",
        {
            "page_title": "Настройки профиля — CupOfQ",
            "form": form,
            "profile_user_display": display_name,
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect(
        get_safe_logout_redirect(request, fallback=reverse("index"))
    )


def public_user_view(request, username: str):
    user = get_object_or_404(
        User.objects.select_related("profile"), username=username
    )
    Profile.objects.get_or_create(user=user)
    q_n = user.questions.count()
    a_n = user.answers.count()
    return render(
        request,
        "core/public_user.html",
        {
            "page_title": f"{user_display_name(user)} — CupOfQ",
            "profile_user": user,
            "profile_user_display": user_display_name(user),
            "questions_count": q_n,
            "answers_count": a_n,
        },
    )


def layout_demo(request):
    return render(
        request,
        "core/layout.html",
        {
            "page_title": "Базовый шаблон — CupOfQ",
        },
    )


@require_GET
def centrifugo_token_view(request):
    question_id_raw = (request.GET.get("question_id") or "").strip()
    if not question_id_raw.isdigit():
        return JsonResponse({"error": "question_id required"}, status=400)

    question_id = int(question_id_raw)
    if request.user.is_authenticated:
        sub = str(request.user.pk)
    else:
        sub = ""

    channel = question_channel(question_id)
    token = make_connection_token(sub, subs={channel: {}})
    return JsonResponse(
        {
            "token": token,
            "ws_url": settings.CENTRIFUGO_WS_URL,
            "namespace": settings.CENTRIFUGO_NAMESPACE,
            "channel": channel,
        }
    )
