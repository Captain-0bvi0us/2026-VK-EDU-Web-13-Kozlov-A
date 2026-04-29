from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    autocomplete_fields = ["author"]
    show_change_link = True
    readonly_fields = ["created_at"]
    fields = ["author", "text", "is_correct", "created_at"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "created_at"]
    list_select_related = ["author"]
    list_prefetch_related = ["tags"]
    search_fields = ["title", "text", "author__username"]
    list_filter = ["created_at", "tags"]
    autocomplete_fields = ["author"]
    filter_horizontal = ["tags"]
    inlines = [AnswerInline]
    readonly_fields = ["created_at"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "author", "is_correct", "created_at"]
    list_select_related = ["question", "author"]
    search_fields = ["text", "question__title", "author__username"]
    list_filter = ["is_correct", "created_at"]
    autocomplete_fields = ["question", "author"]
    readonly_fields = ["created_at"]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "question", "created_at"]
    list_select_related = ["user", "question"]
    search_fields = ["user__username", "question__title"]
    list_filter = ["created_at"]
    autocomplete_fields = ["user", "question"]
    readonly_fields = ["created_at"]


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "answer", "created_at"]
    list_select_related = ["user", "answer", "answer__question"]
    search_fields = ["user__username", "answer__text", "answer__question__title"]
    list_filter = ["created_at"]
    autocomplete_fields = ["user", "answer"]
    readonly_fields = ["created_at"]
