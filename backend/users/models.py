from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import UsernameValidator, validate_not_me


class User(AbstractUser):
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        db_index=True,
        validators=[
            validate_not_me,
            UsernameValidator,
        ],
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )

    first_name = models.CharField(
        "Имя",
        max_length=150,
    )

    last_name = models.CharField(
        "Фамилия",
        max_length=150,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=("username", "email"), name="unique_username_email"
            )
        ]

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        to=User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        to=User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="author",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "follower"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("follower")),
                name="no_self_follow",
            ),
        ]

    def __str__(self) -> str:
        return f"Пользователь {self.follower}, подписался на {self.author}"
