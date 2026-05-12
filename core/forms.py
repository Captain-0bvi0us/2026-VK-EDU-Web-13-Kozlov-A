from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile

from .avatar_validators import (
    AVATAR_MAX_BYTES,
    avatar_extension_validator,
    validate_avatar_max_size,
)
from .models import Profile
from .signup_staging import delete_staged

_AVATAR_HELP_MB = AVATAR_MAX_BYTES // (1024 * 1024)


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "class": "form-control",
                "placeholder": "Введите логин",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "••••••••",
            }
        ),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Вы ввели неверный логин или пароль.",
    }

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class SignupForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        min_length=3,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "username",
                "pattern": "[a-zA-Z0-9_]+",
            }
        ),
        help_text="Латиница, цифры и подчёркивание, 3–150 символов.",
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"}
        ),
    )
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "given-name"}
        ),
        help_text="Как вас будут видеть другие участники.",
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "family-name"}
        ),
        help_text="Можно оставить пустым.",
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
        help_text="Сложный пароль по правилам сайта.",
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
    )
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        validators=[avatar_extension_validator],
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": "image/jpeg,image/png,.jpg,.jpeg,.png"}
        ),
        help_text=(
            f"Необязательно. Только JPEG или PNG, не больше {_AVATAR_HELP_MB} МБ."
        ),
    )

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if f:
            validate_avatar_max_size(f)
        return f

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("Этот логин уже занят.")
        if not username.replace("_", "").isalnum():
            raise ValidationError("Допустимы только латиница, цифры и подчёркивание.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            validate_password(password1)
        return password1

    def clean(self):
        data = super().clean()
        p1 = data.get("password1")
        p2 = data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают.")
        return data

    def save(self, staged_avatar: dict | None = None):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name") or "",
        )
        profile = Profile.objects.get(user=user)
        upload = self.cleaned_data.get("avatar")
        if upload:
            profile.avatar = upload
            profile.save()
            delete_staged(staged_avatar)
        elif staged_avatar:
            path = staged_avatar.get("path")
            name = staged_avatar.get("original_name") or "avatar.jpg"
            if path and default_storage.exists(path):
                with default_storage.open(path, "rb") as f:
                    profile.avatar.save(name, File(f), save=True)
                default_storage.delete(path)
        return user


class ProfileEditForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="Новый аватар",
        required=False,
        validators=[avatar_extension_validator],
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": "image/jpeg,image/png,.jpg,.jpeg,.png"}
        ),
        help_text=(
            f"Заменить фото. Только JPEG или PNG, не больше {_AVATAR_HELP_MB} МБ. "
            "Квадратное изображение смотрится лучше."
        ),
    )
    remove_avatar = forms.BooleanField(
        label="Удалить текущий аватар",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "d-none",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        labels = {
            "email": "Email",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "autocomplete": "email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "given-name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "family-name"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        profile, _ = Profile.objects.get_or_create(user=user)
        self._profile = profile
        super().__init__(*args, instance=user, **kwargs)
        self.fields["avatar"].initial = profile.avatar

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if f:
            validate_avatar_max_size(f)
        return f

    def clean(self):
        data = super().clean()
        if data.get("remove_avatar") and self.files.get("avatar"):
            self.add_error(
                "avatar",
                "Уберите новый файл из поля «Новый аватар» или не нажимайте «Удалить аватар».",
            )
        return data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if not commit:
            return user
        if self.cleaned_data.get("remove_avatar"):
            if self._profile.avatar:
                self._profile.avatar.delete(save=False)
            self._profile.avatar = None
        else:
            upload = self.cleaned_data.get("avatar")
            if isinstance(upload, UploadedFile):
                self._profile.avatar = upload
        self._profile.save()
        return user
