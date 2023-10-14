from typing import List, Dict

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
        """
        Дополнительно проверяет чтобы тег состоял только
        из букв верхнего регистра.
        """
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

    @staticmethod
    def get_ingredients(obj: Recipe) -> List[Dict]:
        """Возвращает список ингредиентов рецепта в виде списка словарей."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeessentials__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Указывает, добавлен ли рецепт в избранное текущим пользователем."""
        return ((user := self.context.get('request').user)
                and user.is_authenticated
                and Favorite.objects.filter(user=user,
                                            recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Указывает, добавлен ли рецепт в корзину текущим пользователем."""
        return ((user := self.context.get('request').user)
                and user.is_authenticated
                and ShoppingCart.objects.filter(user=user,
                                                recipe=recipe).exists())


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

    def to_representation(self, instance: Recipe) -> Dict:
        """Преобразует ингредиенты в словарь с данными из списка словарей."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    @staticmethod
    def create_recipe_essentials(recipe: Recipe,
                                 ingredients: List[Dict]) -> None:
        """Создает связи между рецептом и ингредиентами (RecipeEssentials)."""
        essentials = []
        for ingredient in ingredients:
            try:
                ingredient_obj = Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "ingredients": f'Ингредиента с ID {ingredient["id"]}'
                                       f' не существует.'})

            composition = RecipeEssentials(
                ingredient=ingredient_obj,
                recipe=recipe,
                amount=ingredient['amount']
            )
            essentials.append(composition)
        RecipeEssentials.objects.bulk_create(essentials)

    def create(self, validated_data: Dict) -> Recipe:
        """Создает новый рецепт в базе данных."""
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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        tags = validated_data.get('tags', [])
        instance.tags.set(tags)

        ingredients_data = validated_data.get('ingredients', [])
        instance.ingredients.clear()
        self.create_recipe_essentials(instance, ingredients_data)

        instance.save()
        return instance

    def validate(self, data):
        """
        Дополнительная проверяет наличия и количества
        ингредиентов и тегов в рецепте.
        """

        # Проверка на наличие тегов.
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Укажите хотя бы один тег.'})

        # Проверка на наличие ингредиентов.
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Укажите хотя бы один ингредиент.'})

        # Проверка на уникальность тегов.
        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {'tags': 'Теги не могут дублироваться.'})

        # Проверка на уникальность ингредиентов.
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не могут дублироваться.'})

        # Дополнительная проверка ингредиентов на минимальное количество.
        if len(ingredients) < MIN_INGREDIENT_AMOUNT:
            raise ValidationError(
                {"ingredients": f"Нужен минимум "
                                f"{MIN_INGREDIENT_AMOUNT} ингредиент!"})

        # Проверка на пустое поле тегов.
        if not data.get('tags'):
            raise serializers.ValidationError(
                {'tags': 'Поле тегов не может быть пустым.'})

        # Проверка на пустое поле ингредиентов.
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Поле ингредиентов не может быть пустым.'})

        return data

    @staticmethod
    def validate_image(value: str) -> str:
        """Дополнительно проверяет наличие изображения в рецепте."""
        if not value:
            raise ValidationError(
                {'image': 'Нужно изображение!'})
        return value
