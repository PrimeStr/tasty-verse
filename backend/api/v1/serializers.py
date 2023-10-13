from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework.relations import PrimaryKeyRelatedField

from core.constants.recipes import MIN_INGREDIENT_AMOUNT
from recipes.models import (Tag, Recipe, Favorite, ShoppingCart,
                            Ingredient, RecipeEssentials)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Tag.

        Attributes:
            id (int, read-only): Идентификатор тега.
            name (str): Название тега (без символа '#' и в верхнем регистре).
    """

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate(self, data):
        for attr, value in data.items():
            data[attr] = value.strip(" #").upper()
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Ingredient.

        Attributes:
            id (int, read-only): Идентификатор ингредиента.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id',)


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    """
    Краткий сериализатор для модели Recipe.

    Attributes:
        id (int, read-only): Идентификатор рецепта.
        name (str): Название рецепта.
        image (str): Изображение рецепта в формате Base64.
        cooking_time (int): Время приготовления рецепта в минутах.
    """
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
    """
        Сериализатор для полной информации о рецепте (включая ингредиенты).

        Attributes:
            id (int, read-only): Идентификатор рецепта.
            tags (TagSerializer): Сериализатор для тегов рецепта.
            author (UserSerializer): Сериализатор для автора рецепта.
            ingredients (list of dict): Список ингредиентов рецепта.
            image (str): Изображение рецепта в формате Base64.
            is_favorited (bool): Указывает, добавлен ли рецепт в избранное
            текущим пользователем.
            is_in_shopping_cart (bool): Указывает, добавлен ли рецепт в
            корзину текущим пользователем.
    """
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
        """Возвращает список ингредиентов рецепта в виде списка словарей."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeessentials__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Указывает, добавлен ли рецепт в избранное текущим пользователем."""
        return ((user := self.context.get('request').user) and
                user.is_authenticated and
                Favorite.objects.filter(user=user, recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe):
        """Указывает, добавлен ли рецепт в корзину текущим пользователем."""
        return ((user := self.context.get('request').user) and
                user.is_authenticated and
                ShoppingCart.objects.filter(user=user, recipe=recipe).exists())


class RecipeEssentialsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи между моделями Recipe и Ingredient.

    Attributes:
        id (int, write-only): Идентификатор ингредиента.
        amount (int): Количество ингредиента в рецепте.
    """
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeEssentials
        fields = (
            'id',
            'amount',
        )


class RecipePostSerializer(serializers.ModelSerializer):
    """
        Сериализатор для создания рецепта.

        Attributes:
            id (int, read-only): Идентификатор рецепта.
            tags (TagSerializer): Сериализатор для тегов рецепта.
            author (UserSerializer): Сериализатор для автора рецепта.
            ingredients (RecipeEssentialsSerializer): Сериализатор для
            ингредиентов рецепта.
            image (str): Изображение рецепта в формате Base64.
            name (str): Название рецепта.
            text (str): Описание рецепта.
            cooking_time (int): Время приготовления рецепта в минутах.
    """
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
        """Преобразует ингредиенты в словарь с данными из списка словарей."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    def create_recipe_essentials(self, recipe, ingredients):
        """Создает связи между рецептом и ингредиентами (RecipeEssentials)."""
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
        """Создает новый рецепт в базе данных."""
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
        """Дополнительно проверяет наличие ингредиентов в рецепте."""
        if value < MIN_INGREDIENT_AMOUNT:
            raise ValidationError(
                {"ingredients": f"Нужен минимум "
                                f"{MIN_INGREDIENT_AMOUNT} ингредиент!"})
        return value

    def validate_image(self, value):
        """Дополнительно проверяет наличие изображения в рецепте."""
        if not value:
            raise ValidationError(
                {'image': 'Нужно изображение!'})
        return value
