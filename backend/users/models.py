from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .validators import Username_Validator, validate_not_me


class User(AbstractUser):
    email: models.EmailField = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
    )

    username: models.CharField = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        db_index=True,
        validators=[
            validate_not_me,
            Username_Validator,
        ],
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )

    first_name: models.CharField = models.CharField(
        "Имя",
        max_length=150,
    )

    last_name: models.CharField = models.CharField(
        "Фамилия",
        max_length=150,
    )
    password: models.CharField = models.CharField(
        "Пароль",
        max_length=150,
    )

    class Meta:
        verbose_name: str = "Пользователь"
        verbose_name_plural: str = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=("username", "email"), name="unique_username_email"
            )
        ]

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    follower: models.ForeignKey = models.ForeignKey(
        to=User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author: models.ForeignKey = models.ForeignKey(
        to=User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="author",
    )

    class Meta:
        verbose_name: str = "Подписка"
        verbose_name_plural: str = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "follower"],
                name="unique_follow",
            )
        ]

    def __str__(self) -> str:
        return f"Пользователь {self.follower}, подписался на {self.author}"

    def clean(self) -> None:
        if self.follower == self.author:
            raise ValidationError(
                "Пользователь не может подписаться на самого себя."
            )
