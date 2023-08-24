from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User

from .filter import IngredientFilter, RecipeFilter
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    Shopping_CartSerializer,
    TagSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)
from .utils import (
    generate_shopping_cart_txt,
    get_shopping_cart_ingredients,
    send_shopping_cart_txt,
)


class PublicUserViewSet(DjoserUserViewSet, viewsets.ModelViewSet):
    """Представление для работы с публичными данными пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        url_path="subscriptions",
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subscribed_to = self.paginate_queryset(
            User.objects.filter(author__follower=request.user)
        )
        serializer = UserSubscriptionSerializer(subscribed_to, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписаться на пользователя."""
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            message = {"Пользователь не найден."}
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        if request.user == author:
            message = {"Вы не можете подписаться на самого себя"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            subscription, created = Subscription.objects.get_or_create(
                follower=request.user,
                author=author,
            )

            if created:
                message = {f"Вы успешно подписались на {author}"}
                return Response(message, status=status.HTTP_200_OK)
            else:
                message = {"Вы уже подписаны на этого пользователя"}
                return Response(message, status=status.HTTP_200_OK)

        """Отписаться от пользователя."""
        try:
            subscription = Subscription.objects.get(
                follower=request.user, author=author
            )
            subscription.delete()
            message = {f"Вы отписались от {author}"}
            return Response(message, status=status.HTTP_204_NO_CONTENT)

        except Subscription.DoesNotExist:
            message = {f"Вы не подписаны на {author}"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для работы с тегами рецептов.

    Это представление позволяет просматривать теги рецептов.
    Доступ к просмотру разрешен всем (только чтение),
    вносить изменеия могут только админнистраторы.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для работы с ингредиентами.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == "POST":
            data = {"user": user.id, "recipe": recipe.id}
            serializer = FavoriteSerializer(
                data=data,
                context={"request": request},
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(
            Favorite,
            user=user,
            recipe=recipe,
        )
        favorite.delete()
        message = {"message": "Рецепт успешно удалён из избранного."}
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == "POST":
            data = {"user": user.id, "recipe": recipe.id}
            serializer = Shopping_CartSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart = get_object_or_404(
            ShoppingCart,
            user=user,
            recipe=recipe,
        )
        shopping_cart.delete()
        message = {"message": "Рецепт успешно удалён из корзины."}
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Отправляет текстовый файл списка покупок."""

        user = request.user
        ingredients_data = get_shopping_cart_ingredients(user)
        txt_content = generate_shopping_cart_txt(ingredients_data)
        response = send_shopping_cart_txt(txt_content)

        return response
