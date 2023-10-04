from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from api.v1.pagination import CustomPagination
from api.v1.permissions import IsAuthenticated, IsAdminOrReadOnly
from api.v1.serializers import UserSerializer, SubscriptionSerializer, \
    TagSerializer, RecipeSerializer, IngredientSerializer
from recipes.models import Tag, Recipe, Ingredient
from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):
    """Работа с пользователями. Регистрация пользователей,
     Вывод пользователей. У авторизованных пользователей возможность подписки.
     Djoser позволяет переходить по endpoints user и токена"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = (IsAdminOrReadOnly,)
    link_model = Subscription

    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
