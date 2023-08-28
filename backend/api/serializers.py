from django.db.models import F
from django.db.transaction import atomic

from djoser.serializers import UserCreateSerializer

from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

from users.models import Subscription, User

from .utils import create_ingredients, get_tags
from .validators import (
    validate_email,
    validate_favorite_recipe,
    validate_me,
    validate_post_required_fields,
    validate_shopping_cart_recipe,
    validate_username,
)


class UserSerializer(UserCreateSerializer):
    """
    Сериализатор для модели пользователя с дополнительным полем is_subscribed,
    указывающим, подписан ли пользователь на других пользователей.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
        }

        validators = [
            validate_me,
            validate_username,
            validate_email,
        ]

    def get_is_subscribed(self, user):
        """
        Получает информацию о подписке пользователя на других пользователей.

        Args:
            user (User): Объект пользователя.

        Returns:
            bool: True, если пользователь подписан на других пользователей,
            иначе False.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                author=user, follower=request.user
            ).exists()
        return False

    def to_representation(self, instance):
        """
        Преобразует объект пользователя в представление JSON.

        Args:
            instance (User): Объект пользователя.

        Returns:
            dict: Словарь с данными пользователя.
        """
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request:
            if request.method == "POST":
                data.pop("is_subscribed", None)
            if request.method == "GET":
                data.pop("password", None)

        return data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления данных о пользователе, включая информацию
    о его подписках и созданных рецептах.
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_recipes(self, user):
        """
        Получает информацию о рецептах, созданных пользователем.

        Args:
            user (User): Объект пользователя.

        Returns:
            list: Список словарей с данными о рецептах.
        """
        recipes = Recipe.objects.filter(author=user)
        recipes_data = []
        for recipe in recipes:
            recipes_data.append(
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image.url,
                    "cooking_time": recipe.cooking_time,
                }
            )
        return recipes_data

    def get_recipes_count(self, user):
        """
        Получает количество рецептов, созданных пользователем.

        Args:
            user (User): Объект пользователя.

        Returns:
            int: Количество созданных рецептов.
        """
        return Recipe.objects.filter(author=user).count()

    def get_is_subscribed(self, user):
        """
        Получает информацию о подписке пользователя на других пользователей.

        Args:
            user (User): Объект пользователя.

        Returns:
            bool: True, если пользователь подписан на других пользователей,
            иначе False.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                author=user, follower=request.user
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тега, предоставляющий информацию о теге.
    """

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "color",
            "slug",
        ]
        read_only_fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тега, предоставляющий информацию о ингредиенте.
    """

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "measurement_unit",
        ]
        read_only_fields = ["id", "name", "measurement_unit"]


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи между ингредиентом и рецептом.

    Fields:
    - id (int): Уникальный идентификатор ингредиента.
    - amount (int): Количество ингредиента, используемого в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о рецепте."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)

    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_ingredients(self, recipe):
        ingredient = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipeingredient__amount"),
        )

        return ingredient

    def get_is_favorited(self, instance):
        user = self.context.get("request").user
        if user.is_authenticated:
            return instance.favorites.filter(
                user=user, recipe=instance
            ).exists()
        return False

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=instance).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новых рецептов."""

    ingredients = IngredientToRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def validate(self, data):
        validated_data = validate_post_required_fields(self, data)
        return validated_data

    @atomic
    def create(self, validated_data):
        """
        Создает новый рецепт в базе данных.

        Args:
            validated_data (dict): Проверенные данные для создания рецепта.

        Returns:
            Recipe: Созданный рецепт.
        """
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)

        get_tags(self, tags_data, recipe)
        create_ingredients(self, ingredients_data, recipe)

        return recipe

    @atomic
    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.

        Args:
            instance (Recipe): Существующий рецепт для обновления.
            validated_data (dict): Проверенные данные для обновления рецепта.

        Returns:
            Recipe: Обновленный рецепт.
        """
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        get_tags(self, tags_data, instance)
        create_ingredients(self, ingredients_data, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context={"request": self.context.get("request")},
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор полей избранных рецептов и покупок."""

    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Серилизатор для избранных рецептов."""

    class Meta:
        fields = ("recipe", "user")
        model = Favorite

    def validate(self, data):
        validated_data = validate_favorite_recipe(data)
        return validated_data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={"request": self.context.get("request")},
        ).data


class Shopping_CartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta(FavoriteSerializer.Meta):
        fields = ("recipe", "user")
        model = ShoppingCart

    def validate(self, data):
        validated_data = validate_shopping_cart_recipe(data)
        return validated_data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={"request": self.context.get("request")},
        ).data
