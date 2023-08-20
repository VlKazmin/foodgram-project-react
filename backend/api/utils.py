from rest_framework import serializers
from recipes.models import Tag, RecipeIngredient


def get_tags(self, tags_data, obj):
    tags = []
    for tag in tags_data:
        try:
            tag = Tag.objects.get(id=tag.id)
            tags.append(tag)
        except Tag.DoesNotExist:
            raise serializers.ValidationError({"error": "Тег не найден."})

    obj.tags.set(tags)


def create_ingredients(self, ingredients_data, obj):
    obj.recipe_ingredients.all().delete()
    ingredients = []

    for ingredient_data in ingredients_data:
        try:
            ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                    recipe=obj,
                )
            )

        except Exception:
            raise serializers.ValidationError(
                {"error": "Ингредиент не найден."}
            )

    RecipeIngredient.objects.bulk_create(ingredients)


def get_shopping_cart_ingredients(user):
    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user=user
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
    txt_content = "Список покупок:\n\n"
    for ingredient_name, ingredient_info in ingredients_data.items():
        measurement_unit = ingredient_info['measurement_unit']
        amount = ingredient_info['amount']
        txt_content += f"{ingredient_name} ({measurement_unit}) - {amount}\n"

    return txt_content
