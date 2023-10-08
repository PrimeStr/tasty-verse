import django.db.utils
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.v1.filters import IngredientFilter
from api.v1.permissions import IsAuthorOrAdminOrReadOnly
from api.v1.serializers import (TagSerializer, IngredientSerializer,
                                RecipeReadSerializer, RecipePostSerializer,
                                ShortRecipeReadSerializer)
from core.pagination import CustomPagination
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite


class TagsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        if pk is None:
            queryset = Tag.objects.all()
            serializer = TagSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            try:
                tag = Tag.objects.get(id=pk)
                serializer = TagSerializer(tag)
                return Response(serializer.data)
            except Tag.DoesNotExist:
                return Response({'detail': 'Тег не найден!'},
                                status=status.HTTP_404_NOT_FOUND)


class RecipesAPIView(APIView):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination

    def perform_create(self, serializer, **kwargs):
        serializer.save(author=self.request.user)

    def get(self, request):
        queryset = Recipe.objects.select_related('author')
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer_class = RecipeReadSerializer
        serializer = serializer_class(queryset, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = RecipePostSerializer(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipesDetailAPIView(APIView):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get(self, request, pk):
        queryset = get_object_or_404(Recipe, id=pk)
        serializer_class = RecipeReadSerializer
        serializer = serializer_class(queryset,
                                      context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        self.check_object_permissions(request, recipe)
        try:
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
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

    def post(self, request, pk):
        return self.add_recipe(Favorite, request.user, pk)

    def delete(self, request, pk):
        return self.delete_recipe(Favorite, request.user, pk)

    def add_recipe(self, model, user, pk):
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeReadSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except django.db.utils.IntegrityError:
            return Response({'errors': 'Рецепт уже в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete_recipe(self, model, user, pk):
        try:
            obj = model.objects.get(user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'errors': 'Такого рецепта нет в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartAPIView(APIView):

    def post(self, request, pk):
        return self.add_recipe(ShoppingCart, request.user, pk)

    def delete(self, request, pk):
        return self.delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, model, user, pk):
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeReadSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except django.db.utils.IntegrityError:
            return Response({'errors': 'Рецепт уже в корзине!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete_recipe(self, model, user, pk):
        try:
            obj = model.objects.get(user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'errors': 'Такого рецепта нет в корзине!'},
                            status=status.HTTP_400_BAD_REQUEST)


class IngredientsAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class IngredientsDetailAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


# Cтарая версия внизу

# class IngredientsAPIView(APIView):
#     permission_classes = (AllowAny,)
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = IngredientFilter
#     #search_fields = ('^name', 'name')
#
#     def get(self, request, pk=None):
#         if pk is None:
#             queryset = Ingredient.objects.all()
#             serializer = IngredientSerializer(queryset, many=True)
#             return Response(serializer.data)
#         else:
#             try:
#                 ingredient = Ingredient.objects.get(id=pk)
#                 serializer = IngredientSerializer(ingredient)
#                 return Response(serializer.data)
#             except Ingredient.DoesNotExist:
#                 return Response({'detail': 'Ингредиент не найден!'},
#                                 status=status.HTTP_404_NOT_FOUND)
#
#     # def get(self, request):
#     #     queryset = Ingredient.objects.all()
#     #     serializer = IngredientSerializer(queryset, many=True)
#     #     return Response(serializer.data)
