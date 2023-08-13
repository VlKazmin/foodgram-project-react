from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from users.models import User

from .validators import (
    CookingTime_Validator,
    Hex_Validator,
    IngredientAmount_Validator,
    Slug_Validator,
)


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=200,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        verbose_name=_("Цвет в HEX"),
        max_length=7,
        validators=[Hex_Validator],
        help_text=_("Цвет должен быть в формате HEX-кода(например, #49B64E)."),
    )
    slug = models.CharField(
        verbose_name=_("Уникальный слаг"),
        max_length=200,
        unique=True,
        validators=[Slug_Validator],
    )

    class Meta:
        verbose_name = _("Тэг")
        verbose_name_plural = _("Тэги")
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} (цвет: {self.color})"


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name=_("Автор рецепта"),
        to=User,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=200,
        unique=True,
    )
    image = models.ImageField(
        verbose_name=_("Картинка, закодированная в Base64"),
        upload_to="recipes_image/",
    )
    text = models.TextField(
        verbose_name=_("Описание"),
    )
    ingredients = models.ManyToManyField(
        verbose_name=_("Список ингредиентов"),
        to="Ingredient",
        through="RecipeIngredient",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        verbose_name=_("Тег"),
        to=Tag,
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_("Время приготовления в минутах"),
        default=0,
        validators=[
            CookingTime_Validator,
        ],
    )

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")
        ordering = ("-id",)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name=_("Единицы измерения"),
        max_length=200,
    )

    class Meta:
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_name",
            ),
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    name = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_("Количество"),
        default=0,
        validators=[IngredientAmount_Validator],
    )

    class Meta:
        verbose_name = _("Ингредиент для рецепта")
        verbose_name_plural = _("Ингредиенты для рецепта")

    def __str__(self):
        return (
            f"{self.ingredient} ({self.amount} "
            f"{self.ingredient.measurement_unit})"
        )


class BaseModel(models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name=_("Рецепт"),
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    created_at = models.DateTimeField(
        _("Дата добавления"),
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Favorite(BaseModel):
    class Meta:
        verbose_name = _("Избранный рецепт")
        verbose_name_plural = _("Избранные рецепты")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            )
        ]


class Shopping_Cart(BaseModel):
    class Meta:
        verbose_name = _("Элемент корзины")
        verbose_name_plural = _("Элементы корзины")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_recipe_cart"
            )
        ]
