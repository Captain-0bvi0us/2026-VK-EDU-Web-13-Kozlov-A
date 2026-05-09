from django.shortcuts import redirect, render


def login_view(request):
    if request.method == "POST":
        return redirect("login")
    return render(
        request,
        "core/login.html",
        {
            "page_title": "Вход — CupOfQ",
            "nav_variant": "guest",
        },
    )


def signup(request):
    if request.method == "POST":
        return redirect("signup")
    return render(
        request,
        "core/signup.html",
        {
            "page_title": "Регистрация — CupOfQ",
            "nav_variant": "guest",
        },
    )


def profile(request):
    if request.method == "POST":
        return redirect("profile")
    return render(
        request,
        "core/profile.html",
        {
            "page_title": "Настройки профиля — CupOfQ",
            "nav_variant": "user",
        },
    )


def layout_demo(request):
    return render(
        request,
        "core/layout.html",
        {
            "page_title": "Базовый шаблон — CupOfQ",
            "nav_variant": "user",
        },
    )
