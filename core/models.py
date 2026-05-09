from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="пользователь",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="аватар",
    )

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self) -> str:
        return f"Профиль {self.user.get_username()}"
