from django.core.validators import RegexValidator, MinValueValidator


class Slug_Validator(RegexValidator):
    regex = r"^[-a-zA-Z0-9_]+$"
    message = (
        "Слаг может содержать только буквы, цифры, "
        "знаки минус, подчеркивания и без пробелов.",
    )


class Hex_Validator(RegexValidator):
    regex = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    message = "Цвет должен быть в формате HEX-кода (например, #49B64E).",

    def __call__(self, value):
        return bool(self.regex.search(value))


class CookingTime_Validator:
    def __init__(self, min_value=1, max_value=360):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if value < self.min_value:
            raise ValueError(
                f"Время приготовления не может быть меньше "
                f"{self.min_value} минуты."
            )
        if value > self.max_value:
            raise ValueError(
                f"Время приготовления не должно превышать "
                f"{self.max_value} минут."
            )


class IngredientAmount_Validator(MinValueValidator):
    limit_value = (1,)
    message = f"Количество не может быть меньше {limit_value}"
