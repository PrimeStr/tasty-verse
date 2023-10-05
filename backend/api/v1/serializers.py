from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import PrimaryKeyRelatedField

from backend.settings import EMAIL_LENGTH
from recipes.models import Tag, Recipe, Favorite, ShoppingCart, Ingredient, \
    RecipeEssentials
from users.models import User, Subscription
from users.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания переопределенного User и
    проверки просмотра подписок."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        # поле "password" будет доступно только для записи 
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """вввв"""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, target_user):
        """Проверка подписки пользователей. Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя(True or False)."""
        subscriber = self.context.get('request').user
        if subscriber.is_anonymous:
            return False
        return Subscription.objects.filter(subscriber=subscriber, target_user=target_user).exists()





class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate(self, data):
        for attr, value in data.items():
            data[attr] = value.strip(" #").upper()

        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта.
    image позволяет передавать изображения в виде base64-строки по API."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeessentials__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeEssentialsSerializer(serializers.ModelSerializer): # Переделать
    """Сериализатор для получения состава блюда."""
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeEssentials
        fields = (
            'id',
            'ingredient',
            'recipe',
            'amount',
        )


class RecipePostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeEssentialsSerializer()  # Переделать
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'text',
            'cooking_time',
        )

