from typing import Dict, List

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import Recipe
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей.

    Позволяет просматривать, создавать и редактировать пользователей.

    Attributes:
        - is_subscribed (SerializerMethodField): Возвращает информацию о том,
        подписан ли текущий пользователь на пользователя,
        который сериализуется.

    Meta:
        - model (User): Модель пользователя.
        - fields (tuple): Поля, которые будут сериализованы.
        - extra_kwargs (dict): Дополнительные настройки для полей.

    Methods:
        - create(validated_data): Создает нового пользователя.
        - get_is_subscribed(target_user): Возвращает информацию о подписке
        текущего пользователя на целевого пользователя.
    """
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

    def create(self, validated_data: Dict) -> User:
        """
        Создает нового пользователя.

        Args:
            validated_data (dict): Валидированные данные пользователя.

        Returns:
            User: Созданный пользователь.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, target_user: User) -> bool:
        """
        Возвращает информацию о подписке текущего пользователя на
        целевого пользователя.

        Args:
            target_user (User): Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если текущий пользователь подписан на целевого
            пользователя, в противном случае - False.

        """
        return (
                (subscriber := self.context.get('request').user)
                and subscriber.is_authenticated
                and Subscription.objects.filter(
            subscriber=subscriber,
            target_user=target_user
        ).exists()
        )


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


class UserSubscriptionListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка пользователей и их подписок.

    Позволяет просматривать информацию о пользователях, их подписках
    и количестве рецептов.

    Attributes:
        - email (serializers.EmailField): Email пользователя.
        - username (serializers.CharField): Имя пользователя.
        - first_name (serializers.CharField): Имя пользователя.
        - last_name (serializers.CharField): Фамилия пользователя.
        - is_subscribed (SerializerMethodField): Возвращает информацию о том,
        подписан ли текущий пользователь на пользователя,
        который сериализуется.
        - recipes_count (SerializerMethodField): Количество рецептов
        пользователя.
        - recipes (SerializerMethodField): Сериализованные рецепты
        пользователя.

    Meta:
        - model (User): Модель пользователя.
        - fields (tuple): Поля, которые будут сериализованы.

    Methods:
        - get_is_subscribed(target_user): Возвращает информацию о подписке
        текущего пользователя на целевого пользователя.
        - get_recipes_count(author): Возвращает количество
        рецептов пользователя.
        - get_recipes(author): Возвращает сериализованные
        рецепты пользователя.
    """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_subscribed = SerializerMethodField()
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
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, target_user: User) -> bool:
        return (
                (subscriber := self.context.get('request').user)
                and subscriber.is_authenticated
                and Subscription.objects.filter(
            subscriber=subscriber,
            target_user=target_user
        ).exists()
        )

    @staticmethod
    def get_recipes_count(author: User) -> int:
        """
        Возвращает количество рецептов пользователя.

        Args:
            author (User): Пользователь, для которого подсчитывается
            количество рецептов.

        Returns:
            int: Количество рецептов пользователя.
        """
        return author.recipes.count()

    def get_recipes(self, author: User) -> List:
        """
        Возвращает сериализованные рецепты пользователя.

        Args:
            author (User): Пользователь, для которого сериализуются рецепты.

        Returns:
            list: Список сериализованных рецептов пользователя.
        """
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()[:int(limit)] if limit else (
            author.recipes.all())
        serializer = ShortRecipeReadSerializer(recipes, many=True,
                                               read_only=True)
        return serializer.data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.

    Позволяет создавать и валидировать подписки пользователей.

    Attributes:
        - subscriber (int): Идентификатор подписчика.
        - target_user (int): Идентификатор целевого пользователя.
    """

    class Meta:
        model = Subscription
        fields = ['subscriber', 'target_user']
        read_only_fields = ['subscriber', 'target_user']
        extra_kwargs = {
            'subscriber': {'required': False},
            'target_user': {'required': False},
        }

    def create(self, validated_data) -> Subscription:
        """
        Создает новую подписку или возвращает существующую.

        Args:
            validated_data (dict): Валидированные данные.

        Returns:
            Subscription: Созданная или существующая подписка.
        """
        subscriber = self.context['subscriber']
        target_user = self.context['target_user']
        subscription, _ = Subscription.objects.get_or_create(
            subscriber=subscriber,
            target_user=target_user
        )
        return subscription

    def validate(self, data: Dict) -> Dict:
        """
        Проверяет, что пользователь уже подписан или не пытается
        подписаться на самого себя.

        Args:
            data (dict): Данные для валидации.

        Raises:
            ValidationError: Если пользователь пытается подписаться на самого
            себя или уже подписан на целевого пользователя.

        Returns:
            dict: Валидированные данные.
        """
        target_user = self.context['target_user']
        subscriber = self.context['subscriber']
        if Subscription.objects.filter(subscriber=subscriber,
                                       target_user=target_user
                                       ).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        if subscriber == target_user:
            raise ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data

    def to_representation(self, instance: Subscription) -> Dict:
        """
        Преобразует подписку в формат, удобный для отображения.

        Args:
            instance (Subscription): Подписка.

        Returns:
            dict: Валидированные данные для отображения.
        """
        target_user = instance.target_user
        request = self.context.get('request')
        context = {'request': request}
        return UserSubscriptionListSerializer(target_user,
                                              context=context).data
