import os

from tabulate import tabulate

from django.http import HttpResponse

from rest_framework import serializers

from recipes.models import Tag, RecipeIngredient


def get_tags(self, tags_data, obj):
    """
    Устанавливает теги для объекта на основе предоставленных данных.

    Args:
        self: Экземпляр сериализатора.
        tags_data (list): Список объектов тегов или их идентификаторов.
        obj: Объект, для которого устанавливаются теги (например, рецепт).

    Raises:
        serializers.ValidationError: Если один из тегов не найден в БД.

    Returns:
        None
    """
    tags = []
    for tag in tags_data:
        try:
            tag = Tag.objects.get(id=tag.id)
            tags.append(tag)
        except Tag.DoesNotExist:
            raise serializers.ValidationError({"error": "Тег не найден."})

    obj.tags.clear()
    obj.tags.set(tags)


def create_ingredients(self, ingredients_data, instance):
    """
    Создает и связывает ингредиенты с объектом
    на основе предоставленных данных.

    Args:
        self: Экземпляр сериализатора.
        ingredients_data (list): Список данных об ингредиентах,
                                 включая их идентификаторы и количество.
        instance: Объект, с которым связываются ингредиенты (рецепт).

    Raises:
        serializers.ValidationError: Если один из ингредиентов не найден в БД.

    Returns:
        None
    """
    instance.recipe_ingredients.all().delete()

    ingredients = []

    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data["id"]
        amount = ingredient_data["amount"]

        try:
            existing_ingredient = next(
                (i for i in ingredients if i.ingredient == ingredient_id), None
            )

            if existing_ingredient:
                existing_ingredient.amount += amount

            else:
                ingredients.append(
                    RecipeIngredient(
                        ingredient=ingredient_id,
                        amount=amount,
                        recipe=instance,
                    )
                )

        except Exception:
            raise serializers.ValidationError(
                {"error": "Ингредиент не найден."}
            )

    RecipeIngredient.objects.bulk_create(ingredients)


def get_shopping_cart_ingredients(user):
    """
    Получает данные об ингредиентах для списка покупок пользователя.

    Args:
        user: Пользователь, для которого получаются ингредиенты.

    Returns:
        dict: Словарь данных об ингредиентах, включая их наименование,
              единицу измерения и количество.
              Ключами словаря являются наименования ингредиентов.
    """
    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__shoppingcarts__user=user
    )

    ingredients_data = {}

    for recipe_ingredient in recipe_ingredients:
        ingredient_name = recipe_ingredient.ingredient.name
        ingredient_measurement_unit = (
            recipe_ingredient.ingredient.measurement_unit
        )
        ingredient_amount = recipe_ingredient.amount

        if ingredient_name in ingredients_data:
            ingredients_data[ingredient_name]["amount"] += ingredient_amount
        else:
            ingredients_data[ingredient_name] = {
                "measurement_unit": ingredient_measurement_unit,
                "amount": ingredient_amount,
            }

    return ingredients_data


def generate_shopping_cart_txt(ingredients_data):
    """
    Генерирует текстовое представление списка покупок
    на основе данных об ингредиентах.

    Args:
        ingredients_data (dict): Словарь данных об ингредиентах,
        включая их наименование, единицу измерения и количество.

    Returns:
        str: Текстовое представление списка покупок.
    """
    headers = ["Ингредиент", "Единицы измерения", "Количество"]
    rows = []

    for ingredient_name, ingredient_info in ingredients_data.items():
        measurement_unit = ingredient_info["measurement_unit"]
        amount = ingredient_info["amount"]
        rows.append([ingredient_name, measurement_unit, amount])

    # Используем tabulate для форматирования таблицы
    txt_content = tabulate(rows, headers, tablefmt="grid")

    return f"Список покупок:\n\n{txt_content}\n"


def send_shopping_cart_txt(txt_content):
    """Отправляет текстовый файл списка покупок в HTTP-ответе."""
    temp_file_path = "temp_shopping_cart.txt"

    try:
        with open(temp_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(txt_content)

        with open(temp_file_path, "rb") as txt_file:
            response = HttpResponse(txt_file.read(), content_type="text/plain")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{os.path.basename(temp_file_path)}"'

        return response
    finally:
        os.remove(temp_file_path)
