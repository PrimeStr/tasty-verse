from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Tag, Recipe, Favorite, ShoppingCart,
                            Ingredient, RecipeEssentials)
from users.serializers import UserSerializer


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
            'name',
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
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        """"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        return False


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
    id = IntegerField(read_only=True)
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

    def to_representation(self, instance):
        """Преоразование ингредиентов в словарь с данными
        из списка словарей, в Рецепте."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    def create_recipe_essentials(self, recipe, ingredients):
        """"""
        essentials = []
        for ingredient in ingredients:
            composition = RecipeEssentials(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            essentials.append(composition)
        RecipeEssentials.objects.bulk_create(essentials)

    def create(self, validated_data):
        """"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for ingredient in ingredients:
            ingredient = ingredient['id']
            try:
                Ingredient.objects.get(id=ingredient)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {"ingredients": f"Ингредиента с ID {ingredient} "
                                    f"не существует."})

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_essentials(recipe=recipe,
                                      ingredients=ingredients)
        return recipe

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {"ingredients": "Нужен минимум 1 ингредиент!"})
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(
                {'image': 'Нужно изображение!'})
        return value