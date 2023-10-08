from django_filters import FilterSet, CharFilter

from recipes.models import Ingredient
from users.models import User


class UserFilter(FilterSet):
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
    name = CharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )
