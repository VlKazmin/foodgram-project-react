from django.db import models

from colorfield.fields import ColorField

from users.models import User

from .validators import (
    CookingTime_Validator,
    IngredientAmount_Validator,
    SlugValidator,
)


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        unique=True,
        db_index=True,
    )
    color = ColorField(
        verbose_name="Цвет в HEX",
        help_text="Цвет должен быть в формате HEX-кода (например, #49B64E).",
    )
    slug = models.SlugField(
        verbose_name="Уникальный слаг",
        max_length=200,
        unique=True,
        validators=[SlugValidator],
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} (цвет: {self.color})"


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_name_measurement_unit",
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name="Автор рецепта",
        to=User,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        unique=True,
    )
    image = models.ImageField(
        verbose_name="Картинка, закодированная в Base64",
        upload_to="recipes_image/",
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    ingredients = models.ManyToManyField(
        verbose_name="Список ингредиентов",
        to=Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        verbose_name="Тег",
        to=Tag,
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=[
            CookingTime_Validator,
        ],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
        validators=[IngredientAmount_Validator],
    )

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.ingredient} ({self.amount} "
            f"{self.ingredient.measurement_unit})"
        )


class BaseCartItem(models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True


class Favorite(BaseCartItem):
    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            )
        ]


class ShoppingCart(BaseCartItem):
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_recipe_cart"
            )
        ]
