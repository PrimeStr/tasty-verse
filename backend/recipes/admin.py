from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Ingredient, Tag, Recipe,
                            RecipeEssentials, Favorite, ShoppingCart)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настроенная админ-панель Тегов.

    Список отображаемых полей:
        - id
        - name
        - color
        - slug

    Поля для поиска:
        - name

    Фильтры:
        - id
        - name
        - color
    """
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('id', 'name', 'color')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Настроенная админ-панель Рецептов.

    Список отображаемых полей:
        - id
        - author
        - name
        - image
        - text
        - cooking_time

    Поле "Пусто" отображается как "-пусто-".

    Поля для поиска:
        - author

    Фильтры:
        - id
        - author
        - name
        - tags
    """
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time'
    )

    empty_value_display = '-пусто-'
    search_fields = ('author',)
    list_filter = ('id', 'author', 'name', 'tags')


@admin.register(RecipeEssentials)
class RecipeEssentialsAdmin(admin.ModelAdmin):
    """
    Настроенная админ-панель Ингредиентов в рецепте.

    Список отображаемых полей:
        - id
        - recipe
        - ingredient
        - amount

    Поля для поиска:
        - ingredient

    Фильтры:
        - id
        - recipe
        - ingredient
        - amount
    """
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('ingredient',)
    list_filter = ('id', 'recipe', 'ingredient', 'amount')


class IngredientResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта ингредиентов.

    Мета:
        - model (Ingredient): Модель ингредиента для импорта/экспорта.
    """
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    """
    Настроенная админ-панель Ингредиентов.

    Ресурс класса:
        - IngredientResource: Ресурс для импорта/экспорта ингредиентов.

    Модель ингредиента:
        - id
        - name
        - measurement_unit

    Мета:
        - list_display (tuple): Список отображаемых полей.
        - search_fields (tuple): Поля для поиска.
        - list_filter (tuple): Фильтры.
    """
    resource_classes = [IngredientResource]

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('id', 'name', 'measurement_unit')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Настроенная админ-панель избранных рецептов у пользователей.

    Список отображаемых полей:
        - user
        - recipe

    Фильтры:
        - user
        - recipe
    """
    list_display = (
        'user',
        'recipe',
        'add_date'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Настроенная админ-панель корзин покупок у пользователей.

    Список отображаемых полей:
        - user
        - recipe

    Фильтры:
        - user
        - recipe
    """
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
