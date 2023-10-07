from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import PrimaryKeyRelatedField

from backend.settings import EMAIL_LENGTH
from recipes.models import (Tag, Recipe, Favorite, ShoppingCart,
                            Ingredient, RecipeEssentials)
from users.models import User, Subscription
from users.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    """"""
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
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """"""
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
        """"""
        subscriber = self.context.get('request').user
        return Subscription.objects.filter(subscriber=subscriber,
                                           target_user=target_user).exists()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """"""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, author):
        """"""
        return author.recipes.count()

    def get_recipes_count(self, author):
        """"""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()[
                  :int(limit)] if limit else author.recipes.all()
        serializer = ShortRecipeReadSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        """"""
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя себя!'
            )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data


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
        read_only_fields = ('id',)


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    """"""
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
        """"""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeessentials__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeEssentialsSerializer(serializers.ModelSerializer):
    """"""
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeEssentials
        fields = (
            'id',
            'amount',
        )


class RecipePostSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = RecipeEssentialsSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create_recipe_essentials(self, recipe, ingredients):
        """"""
        compositions = []
        for ingredient in ingredients:
            composition = RecipeEssentials(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            compositions.append(composition)
        RecipeEssentials.objects.bulk_create(compositions)

    def create(self, validated_data):
        """"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_essentials(recipe=recipe,
                                      ingredients=ingredients)
        return recipe

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {'ingredients': 'Нужен минимум 1 ингредиент!'})
        return value
