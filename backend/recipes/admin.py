from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import Ingredient, Tag, Recipe, RecipeEssentials, Favorite, ShoppingCart



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Тегов."""

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
    """Настроенная админ-панель Тегов."""
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
    """Настроенная админ-панель Ингредиенты в рецепте."""
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('ingredient',)
    list_filter = ('id', 'recipe', 'ingredient', 'amount')


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResource]

admin.site.register(Ingredient, IngredientAdmin)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настроенная админ-панель избранные рецепты у пользователей."""
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настроенная админ-панель корзин покупок у пользователей."""
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)