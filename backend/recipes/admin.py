from django.contrib import admin
from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    Shopping_Cart,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    list_filter = ("author",)
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "amount", "name")
    search_fields = ("ingredient__name",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    list_filter = ("user", "recipe")
    search_fields = ("user__email",)


@admin.register(Shopping_Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    list_filter = ("user", "recipe")
    search_fields = ("user__email",)
