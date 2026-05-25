"""URL-адреса приложения core"""

from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
    path("user/<str:username>/", views.public_user_view, name="public_user"),
    path("layout/", views.layout_demo, name="layout"),
    path("api/centrifugo/token/", views.centrifugo_token_view, name="centrifugo_token"),
]
