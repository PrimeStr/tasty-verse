from typing import Any

from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.filters import IngredientFilter, RecipeFilter
from api.v1.permissions import IsAuthorOrAdminOrAuthenticatedOrReadOnly
from api.v1.serializers import (IngredientSerializer, RecipePostSerializer,
                                RecipeReadSerializer, TagSerializer)
from api.v1.shopping_cart_in_pdf import generate_shopping_list_pdf
from core.pagination import CustomPagination
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.serializers import ShortRecipeReadSerializer


class TagsAPIView(APIView):
    """
    API endpoint для работы с тегами рецептов.

    GET:
        Получение списка всех тегов или конкретного тега по id.

    Args:
        pk (int, optional): Идентификатор тега.

    Returns:
        Response: JSON-сериализованный список тегов или информация
        о конкретном теге.
    """
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request: Any, pk: Any = None) -> Response:
        if pk is None:
            queryset = Tag.objects.all()
            serializer = TagSerializer(queryset, many=True)
            return Response(serializer.data)
        tag = get_object_or_404(Tag, id=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class RecipesAPIView(APIView):
    """
    API endpoint для работы с рецептами.

    GET:
        Получение списка рецептов с возможностью фильтрации.

    POST:
        Создание нового рецепта.

    Args:
        pk (int, optional): Идентификатор рецепта.

    Returns:
        Response: JSON-сериализованный список рецептов или информация
        о конкретном рецепте.

    """
    permission_classes = (IsAuthorOrAdminOrAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer, **kwargs: Any) -> None:
        serializer.save(author=self.request.user)

    def get(self, request) -> Response:
        queryset = Recipe.objects.select_related('author')
        filterset = RecipeFilter(request.query_params, queryset=queryset,
                                 request=request)
        queryset = filterset.qs
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer_class = RecipeReadSerializer
        serializer = serializer_class(queryset, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @staticmethod
    def post(request) -> Response:
        serializer = RecipePostSerializer(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipesDetailAPIView(APIView):
    """
    API endpoint для работы с конкретным рецептом.

    GET:
        Получение информации о конкретном рецепте.

    DELETE:
        Удаление конкретного рецепта.

    PATCH:
        Обновление конкретного рецепта.

    Args:
        pk (int): Идентификатор рецепта.

    Returns:
        Response: JSON-сериализованная информация о рецепте.

    """
    permission_classes = (IsAuthorOrAdminOrAuthenticatedOrReadOnly,)

    @staticmethod
    def get(request: Any, pk: Any) -> Response:
        queryset = get_object_or_404(Recipe, id=pk)
        serializer_class = RecipeReadSerializer
        serializer = serializer_class(queryset,
                                      context={'request': request})
        return Response(serializer.data)

    def delete(self, request: Any, pk: Any) -> Response:
        recipe = get_object_or_404(Recipe, id=pk)
        self.check_object_permissions(request, recipe)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk: Any) -> Response:
        recipe = get_object_or_404(Recipe, id=pk)
        self.check_object_permissions(request, recipe)
        serializer = RecipePostSerializer(recipe,
                                          data=request.data,
                                          partial=True,
                                          context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoritesAPIView(APIView):
    """
    API endpoint для работы с избранными рецептами пользователей.

    POST:
        Добавление рецепта в избранное.

    DELETE:
        Удаление рецепта из избранного.

    Args:
        pk (int): Идентификатор рецепта.

    Returns:
        Response: JSON-сериализованная информация о рецепте.

    """

    def post(self, request, pk: Any) -> Response:
        return self.add_recipe(Favorite, request.user, pk)

    def delete(self, request, pk: Any) -> Response:
        return self.delete_recipe(Favorite, request.user, pk)

    @staticmethod
    def add_recipe(model, user: Any, pk: Any) -> Response:
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeReadSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'errors': 'Рецепт уже в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_recipe(model, user: Any, pk: Any) -> Response:
        try:
            obj = model.objects.get(user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'errors': 'Такого рецепта нет в избранном!'},
                            status=status.HTTP_404_NOT_FOUND)


class ShoppingCartAPIView(APIView):
    """
    API endpoint для работы с корзиной покупок пользователей.

    POST:
        Добавление рецепта в корзину.

    DELETE:
        Удаление рецепта из корзины.

    Args:
        pk (int): Идентификатор рецепта.

    Returns:
        Response: JSON-сериализованная информация о рецепте.
    """

    def post(self, request, pk: Any) -> Response:
        return self.add_recipe(ShoppingCart, request.user, pk)

    def delete(self, request, pk: Any) -> Response:
        return self.delete_recipe(ShoppingCart, request.user, pk)

    @staticmethod
    def add_recipe(model, user: Any, pk: Any) -> Response:
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeReadSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'errors': 'Рецепт уже в корзине!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_recipe(model, user: Any, pk: Any) -> Response:
        try:
            recipe = model.objects.get(user=user, recipe__id=pk)
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'errors': 'Такого рецепта нет в корзине!'},
                            status=status.HTTP_404_NOT_FOUND)


class DownloadShoppingCart(APIView):
    """
    API endpoint для скачивания списка покупок в формате PDF.

    GET:
    Получение списка покупок в формате PDF.

    Returns:
        Response: PDF-файл списка покупок.
    """
    @staticmethod
    def get(request) -> HttpResponse:
        return generate_shopping_list_pdf(request.user)


class IngredientsAPIView(ListAPIView):
    """
    API endpoint для работы с ингредиентами.

    Returns:
        Response: JSON-сериализованный список ингредиентов.
    """
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class IngredientsDetailAPIView(RetrieveAPIView):
    """
    API endpoint для получения информации о конкретном ингредиенте.

    Args:
        pk (int): Идентификатор ингредиента.

    Returns:
        Response: JSON-сериализованная информация о ингредиенте.
    """
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
