import django.db.utils
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from api.v1.pagination import CustomPagination
from api.v1.permissions import IsAdminOrReadOnly
from api.v1.serializers import (UserSerializer, TagSerializer,
                                IngredientSerializer, RecipeReadSerializer,
                                RecipePostSerializer, ShortRecipeReadSerializer,
                                UserSubscriptionSerializer)
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite
from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):
    """"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAdminOrReadOnly,)
    link_model = Subscription

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):   # ValueError: Cannot query "primestr": Must be "Subscription" instance.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """"""
        subscriber = request.user
        queryset = User.objects.filter(subscriber__user=subscriber)
        # pages = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            # pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['get', 'delete', 'post'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        """"""
        subscriber = request.user
        target_user_id = self.kwargs.get('id')
        target_user = get_object_or_404(User, id=target_user_id)

        if request.method == 'POST':
            serializer = UserSubscriptionSerializer(
                target_user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=subscriber, author=target_user)
            return Response('Подписка оформлена',
                            status=status.HTTP_204_NO_CONTENT)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=subscriber,
                author=target_user
            )
            subscription.delete()
            return Response('Подписка удалена', status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsView(APIView):
    def get(self, request):
        user = request.user
        queryset = User.objects.filter(subscribe__user=user)
        serializer = UserSubscriptionSerializer(queryset, many=True,
                                                context={'request': request})
        return Response(serializer.data)


class TagsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)


class RecipesAPIView(APIView):
    permission_classes = (AllowAny,)

    def perform_create(self, serializer, **kwargs):
        serializer.save(author=self.request.user)

    def get(self, request):
        queryset = Recipe.objects.select_related('author')
        serializer_class = RecipeReadSerializer
        serializer = serializer_class(queryset, many=True,
                                      context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoritesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

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


class IngredientsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        queryset = Ingredient.objects.all()
        serializer = IngredientSerializer(queryset, many=True)
        return Response(serializer.data)
