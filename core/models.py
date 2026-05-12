import os
import uuid

from django.conf import settings
from django.db import models


def profile_avatar_upload_to(_instance, filename):
    _, ext = os.path.splitext(filename or "")
    ext = ext.lower()
    if ext == ".jpeg":
        ext = ".jpg"
    if ext not in (".jpg", ".png"):
        ext = ".jpg"
    return f"avatars/{uuid.uuid4().hex}{ext}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="пользователь",
    )
    avatar = models.ImageField(
        upload_to=profile_avatar_upload_to,
        blank=True,
        null=True,
        verbose_name="аватар",
    )

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self) -> str:
        return f"Профиль {self.user.get_username()}"
