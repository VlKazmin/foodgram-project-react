from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    tags = filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="iexact",
    )
    author = filters.CharFilter(
        field_name="author__username",
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
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset.exclude(shopping_carts__user=self.request.user)
