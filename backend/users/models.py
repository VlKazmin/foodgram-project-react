from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    GUEST = "guest", _("Гость")
    USER = "user", _("Пользователь")
    ADMIN = "admin", _("Администратор")


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator(
        regex=r"^[\w]+[^@\.\+\-]*$",
        message=_(
            "Неверное имя пользователя. "
            "Допускаются только буквы, цифры и знак подчеркивания."
            " Не может содержать символы «@», «.», «+» или «-»."
        ),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[username_validator],
        error_messages={
            "unique": _("Пользователь с таким именем уже существует."),
        },
    )

    email = models.EmailField(
        verbose_name=_("Электронная почта"),
        max_length=254,
        unique=True,
    )

    password = models.CharField(
        _("Пароль"),
        max_length=128,
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
