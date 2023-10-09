from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

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

    def create(self, validated_data):
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

    def get_is_subscribed(self, target_user):
        """
        Возвращает информацию о подписке текущего пользователя на
        целевого пользователя.

        Args:
            target_user (User): Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если текущий пользователь подписан на целевого
            пользователя, в противном случае - False.

        """
        subscriber = self.context.get('request').user
        if subscriber.is_authenticated:
            return Subscription.objects.filter(
                subscriber=subscriber, target_user=target_user
            ).exists()
        return False


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя и его подписок.

    Позволяет просматривать информацию о пользователе, его подписках
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
        - validate(data): Проверяет, что пользователь не
        пытается подписаться на самого себя.
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

    def get_is_subscribed(self, target_user):
        """
        Возвращает информацию о подписке текущего пользователя на
        целевого пользователя.

        Args:
            target_user (User или list): Пользователь или список
            пользователей, на которых проверяется подписка.

        Returns:
            bool: True, если текущий пользователь подписан на целевого
            пользователя (или на всех пользователей в списке, если передан
            список), в противном случае - False.
        """
        subscriber = self.context.get('request').user
        if isinstance(target_user, User):
            if subscriber.is_anonymous:
                return False
            return bool(target_user.subscriber.filter(subscriber=subscriber))

        elif isinstance(target_user, list):
            if subscriber.is_anonymous:
                return False
            return Subscription.objects.filter(
                subscriber=subscriber, target_user=target_user
            ).exists()

    def get_recipes_count(self, author):
        """
        Возвращает количество рецептов пользователя.

        Args:
            author (User): Пользователь, для которого подсчитывается
            количество рецептов.

        Returns:
            int: Количество рецептов пользователя.
        """
        return author.recipes.count()

    def get_recipes(self, author):
        """
        Возвращает сериализованные рецепты пользователя.

        Args:
            author (User): Пользователь, для которого сериализуются рецепты.

        Returns:
            list: Список сериализованных рецептов пользователя.
        """
        # Импорт внутри функции для избежания циклического импорта.
        from api.v1.serializers import ShortRecipeReadSerializer

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()[:int(limit)] if limit else (
            author.recipes.all())
        serializer = ShortRecipeReadSerializer(recipes, many=True,
                                               read_only=True)
        return serializer.data

    def validate(self, data):
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
