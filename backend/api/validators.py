from rest_framework import serializers

from users.models import User


def validate_me(data):
    """
    Проверка, что username не равно 'me'.
    """
    if data.get("username") == "me":
        raise serializers.ValidationError("Использовать имя 'me' запрещено")
    return data


def validate_username(data):
    """
    Проверка уникальности username.
    """
    username = data["username"]
    email = data["email"]

    if User.objects.exclude(email=email).filter(username=username).exists():
        raise serializers.ValidationError(
            "Пользователь с таким именем уже существует."
        )
    return data


def validate_email(data):
    """
    Проверка уникальности email.
    """
    username = data["username"]
    email = data["email"]

    if User.objects.exclude(username=username).filter(email=email).exists():
        raise serializers.ValidationError(
            "Пользователь с таким email уже существует."
        )
    return data


def validate_is_subscribed(data):
    """
    Проверка невозможности подписаться на самого себя.
    """
    follower = data.context.get("request").user
    author = data["username"]

    if author == follower:
        raise serializers.ValidationError(
            "Пользователь не может подписаться на самого себя."
        )

    return data


def validate_post_required_fields(self, data):
    """
    Проверка наличия требуемых полей.
    """
    request_method = self.context.get("request").method

    if request_method in ["POST"]:
        required_fields = [
            "image",
            "name",
            "text",
            "cooking_time",
            "ingredients",
            "tags",
        ]

        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(
                    [f"{field} - это поле обязательно для создания рецепта."]
                )

    return data


def validate_favorite_recipe(data):
    """Проверка уникальности рецептов в избранном."""
    user = data["user"]
    if user.favorites.filter(recipe=data["recipe"]).exists():
        raise serializers.ValidationError("Рецепт уже добавлен в избранное.")
    return data


def validate_shopping_cart_recipe(data):
    """Проверка уникальности рецептов в корзине."""
    user = data["user"]
    if user.shoppingcarts.filter(recipe=data["recipe"]).exists():
        raise serializers.ValidationError(
            "Рецепт уже добавлен в список покупок."
        )
    return data
