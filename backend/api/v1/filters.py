from django_filters import (FilterSet, CharFilter,
                            ModelMultipleChoiceFilter, NumberFilter)

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    """
    Настраиваемые фильтры для рецептов.

    Позволяет фильтровать рецепты по тегам, авторам, а также по наличию
    в избранном или корзине определенного пользователя.

    Attributes:
        - is_favorited (NumberFilter): Фильтр для проверки наличия рецепта в избранном пользователя.
        - is_in_shopping_cart (NumberFilter): Фильтр для проверки наличия рецепта в корзине пользователя.
        - tags (ModelMultipleChoiceFilter): Фильтр по тегам.
    """

    is_favorited = NumberFilter(
        field_name='favorites_recipe__user',
        method='filter_users_lists',
        label='is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        field_name='shopping_recipe__user',
        method='filter_users_lists',
        label='is_in_shopping_cart'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_users_lists(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not int(value):
            return queryset
        return queryset.filter(**{name: user})


class UserFilter(FilterSet):
    """
    Настраиваемые фильтры для пользователей.

    Позволяет фильтровать пользователей по имени и email.

    Attributes:
        - username (CharFilter): Фильтр по имени пользователя (по частичному совпадению).
        - email (CharFilter): Фильтр по email пользователя (по частичному совпадению).
    """
    username = CharFilter(
        lookup_expr='icontains'
    )
    email = CharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class IngredientFilter(FilterSet):
    """
    Настраиваемые фильтры для ингредиентов.

    Позволяет фильтровать ингредиенты по названию.

    Attributes:
        - name (CharFilter): Фильтр по названию ингредиента (по частичному совпадению).

    Meta:
        - model (Ingredient): Связанная модель, по которой осуществляется фильтрация.
        - fields (tuple): Поля модели `Ingredient`, по которым можно осуществлять фильтрацию.
    """
    name = CharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )
