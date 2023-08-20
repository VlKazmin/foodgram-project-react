from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    Favorite,
    ShoppingCart,
)
from users.models import Subscription, User

from .utils import create_ingredients, get_tags
from .validators import (
    validate_email,
    validate_me,
    validate_post_required_fields,
    validate_username,
)


class UserBaseSerializer(serializers.ModelSerializer):
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
        ]

        validators = [
            validate_me,
            validate_username,
            validate_email,
        ]

    def get_is_subscribed(self, user):
        return Subscription.objects.filter(author=user).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request:
            if request.method == "POST":
                data.pop("is_subscribed", None)

        return data


class UserSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserSubscriptionSerializer(UserBaseSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["recipes", "recipes_count"]

    def get_recipes(self, user):
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
        return Recipe.objects.filter(author=user).count()


class TagSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "measurement_unit",
        ]
        read_only_fields = ["id", "name", "measurement_unit"]


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
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
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        try:
            recipe = Recipe.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

        get_tags(self, tags_data, recipe)
        create_ingredients(self, ingredients_data, recipe)

        return recipe

    @atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        get_tags(self, tags_data, instance)
        create_ingredients(self, ingredients_data, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class ReadRecipeSerializer(serializers.ModelSerializer):
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
        return user.favorites.filter(recipe=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get("request").user
        return user.shopping_carts.filter(recipe=instance).exists()


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
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в избранное."
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class Shopping_CartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta(FavoriteSerializer.Meta):
        fields = ("recipe", "user")
        model = ShoppingCart

    def validate(self, data):
        user = data["user"]
        if user.shopping_carts.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в список покупок."
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data
