from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from api.v1.pagination import CustomPagination
from api.v1.permissions import IsAuthenticated, IsAdminOrReadOnly
from api.v1.serializers import UserSerializer, \
    TagSerializer, IngredientSerializer, RecipeReadSerializer, \
    RecipePostSerializer, ShortRecipeReadSerializer
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite
from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):
    """"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = (IsAdminOrReadOnly,)
    link_model = Subscription



class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    #serializer_class = RecipeSerializer

    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipePostSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """"""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """"""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, model, user, pk):
        """"""

        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        """"""
        try:
            obj = model.objects.get(user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'errors': 'Такого рецепта не существует!'},
                            status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
