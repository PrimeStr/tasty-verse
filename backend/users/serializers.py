from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from users.models import User, Subscription


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
        if subscriber.is_authenticated:
            return Subscription.objects.filter(
                subscriber=subscriber, target_user=target_user
            ).exists()
        return False


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
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

    def get_recipes_count(self, author):
        """"""
        return author.recipes.count()

    def get_recipes(self, author):
        """"""
        # Импорт внутри функции для избежания циклического импорта.
        from api.v1.serializers import ShortRecipeReadSerializer

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()[
                  :int(limit)] if limit else author.recipes.all()
        serializer = ShortRecipeReadSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        """"""
        target_user = self.instance
        subscriber = self.context.get('request').user
        if Subscription.objects.filter(target_user=target_user,
                                       subscriber=subscriber).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        if subscriber == target_user:
            raise ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data
