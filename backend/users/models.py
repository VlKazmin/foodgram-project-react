from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import CustomUsernameValidator


class Role(models.TextChoices):
    GUEST = "guest", _("Гость")
    USER = "user", _("Пользователь")
    ADMIN = "admin", _("Администратор")


class User(AbstractUser):
    email = models.EmailField(
        _("Электронная почта"),
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        _("Имя пользователя"),
        max_length=150,
        unique=True,
        db_index=True,
        validators=[CustomUsernameValidator],
        error_messages={
            "unique": _("Пользователь с таким именем уже существует."),
        },
    )

    first_name = models.CharField(
        _("Имя"),
        max_length=150,
    )

    last_name = models.CharField(
        _("Фамилия"),
        max_length=150,
    )
    password = models.CharField(
        _("Пароль"),
        max_length=150,
    )

    role = models.CharField(
        _("Роль"),
        max_length=50,
        choices=Role.choices,
        default=Role.GUEST,
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("username",)
        constraints = [
            models.UniqueConstraint(
                fields=("username", "email"), name="unique_username_email"
            )
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        _("Подписчик"),
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    following = models.ForeignKey(
        _("Автор"),
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["following", "follower"], name="unique_follow"
            )
        ]

    def __str__(self):
        return f"Пользователь {self.follower}, подписался на {self.following}"
