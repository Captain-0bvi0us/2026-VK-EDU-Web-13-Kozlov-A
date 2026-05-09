from django import forms
from django.utils.text import slugify

from .models import Answer, Question, Tag


MAX_TAGS = 5


class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        label="Теги",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "через запятую",
            }
        ),
        help_text="До 5 тегов через запятую. Будут созданы при необходимости.",
    )

    class Meta:
        model = Question
        fields = ("title", "text")
        labels = {
            "title": "Заголовок",
            "text": "Текст",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 255},
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "maxlength": 30000,
                }
            ),
        }

    def __init__(self, *args, author=None, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def clean_tags_input(self):
        raw = self.cleaned_data.get("tags_input") or ""
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if len(parts) > MAX_TAGS:
            raise forms.ValidationError(f"Не больше {MAX_TAGS} тегов.")
        for name in parts:
            if len(name) > 64:
                raise forms.ValidationError(
                    "Каждый тег не длиннее 64 символов."
                )
        return parts

    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author
        tag_names = self.cleaned_data["tags_input"]
        if commit:
            question.save()
            tags = [self._get_or_create_tag(name) for name in tag_names]
            question.tags.set(tags)
        return question

    def _get_or_create_tag(self, name: str) -> Tag:
        name = name.strip()[:64]
        found = Tag.objects.filter(name=name).first()
        if found:
            return found
        base = slugify(name, allow_unicode=True)[:64] or "tag"
        slug = base
        i = 1
        while Tag.objects.filter(slug=slug).exists():
            i += 1
            slug = f"{base}-{i}"[:64]
        return Tag.objects.create(name=name, slug=slug)


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        labels = {"text": "Текст ответа"}
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "maxlength": 10000,
                    "placeholder": "Напишите развёрнутый ответ…",
                }
            ),
        }

    def __init__(self, *args, author=None, question=None, **kwargs):
        self.author = author
        self.question = question
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question
        if commit:
            answer.save()
        return answer
