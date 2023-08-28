from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов, позволяющий осуществлять поиск и фильтрацию
    на основе различных параметров, таких как теги, автор, избранное и корзина.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    author = filters.CharFilter(
        field_name="author__id",
        lookup_expr="iexact",
    )
    is_favorited = filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.NumberFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = [
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты на основе избранного пользователя."""
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты на основе наличия в корзине пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset.exclude(shoppingcarts__user=self.request.user)


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов, позволяющийосуществлять поиск
       по имени ингредиента.
    """

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
