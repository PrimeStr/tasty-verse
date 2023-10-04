from django.db.models import F
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from backend.settings import EMAIL_LENGTH
from recipes.models import Tag, Recipe, Favorite, ShoppingCart, Ingredient
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


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate(self, data):
        for attr, value in data.items():
            data[attr] = value.strip(" #").upper()

        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredients_in_recipe__amount')
        )
        return ingredients


    def get_is_favorited(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and Favorite.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
                self.context.get('request').user.is_authenticated and
                ShoppingCart.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


