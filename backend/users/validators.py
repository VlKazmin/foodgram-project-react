from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUsernameValidator(UnicodeUsernameValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = _(
            "Неверное имя пользователя. "
            "Допускаются только буквы, цифры и знак подчеркивания."
            " Не может содержать символы «@», «.», «+» или «-»."
        )

    def __call__(self, value):
        if value.lower() == "me":
            raise ValidationError(_("Имя пользователя 'me' недопустимо."))
