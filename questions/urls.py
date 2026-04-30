from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag>/", views.tag, name="tag"),
    path("question/<int:pk>/", views.question_detail, name="question_detail"),
    path("question/<int:pk>/vote/", views.question_vote, name="question_vote"),
    path("answer/<int:pk>/vote/", views.answer_vote, name="answer_vote"),
    path("answer/<int:pk>/correct/", views.mark_answer_correct, name="mark_answer_correct"),
    path("ask/", views.ask, name="ask"),
]
