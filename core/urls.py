"""URL-адреса приложения core"""

from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("layout/", views.layout_demo, name="layout"),
]
