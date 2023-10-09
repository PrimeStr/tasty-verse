from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.filters import UserFilter
from api.v1.permissions import IsAdminOrReadOnly
from core.pagination import CustomPagination
from users.models import Subscription, User
from users.serializers import UserSerializer, UserSubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    """
    Настраиваемый ViewSet для пользователей.

    Позволяет просматривать, создавать и редактировать пользователей,
    а также управлять подписками и получать список подписчиков.

    Attributes:
        - queryset (QuerySet): Набор всех пользователей.
        - serializer_class (Serializer): Сериализатор для пользователей.
        - permission_classes (tuple): Кортеж с классами разрешений.
        - pagination_class (CustomPagination): Класс пагинации.
        - link_model (Subscription): Модель для связи с подписками.
        - filter_backends (tuple): Кортеж с классами фильтрации.
        - filterset_class (UserFilter): Класс фильтра для пользователей.

    Actions:
        - subscriptions: Получение списка подписок текущего пользователя.
        - subscribe: Управление подписками на других пользователей.
        - me: Получение данных о текущем пользователе.

    Methods:
        - subscriptions(request): Метод для действия `subscriptions`.
        - subscribe(request, **kwargs): Метод для действия `subscribe`.
        - me(request): Метод для действия `me`.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    link_model = Subscription
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """
        Получение списка подписок текущего пользователя.

        Args:
            request (Request): Запрос.

        Returns:
            Response: Список подписок с данными о пользователях.
        """
        subscriber = request.user
        queryset = User.objects.filter(subscriber__subscriber=subscriber)
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)

        serializer = UserSubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['delete', 'post'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        """
        Управление подписками на других пользователей.

        Args:
            request (Request): Запрос.
            kwargs: Параметры запроса, включая ID целевого пользователя.

        Returns:
            Response: Статус операции или данные о пользователе
            (при создании подписки).
        """
        subscriber = request.user
        target_user_id = self.kwargs.get('id')
        target_user = get_object_or_404(User, id=target_user_id)

        if request.method == 'POST':
            serializer = UserSubscriptionSerializer(
                target_user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(subscriber=subscriber,
                                        target_user=target_user)
            serializer = UserSubscriptionSerializer(
                target_user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                subscriber=subscriber,
                target_user=target_user
            )

            if subscription.exists():
                subscription.delete()
                return Response('Подписка удалена',
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response('Подписка не найдена',
                                status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """
        Получение данных о текущем пользователе.

        Args:
            request (Request): Запрос.

        Returns:
            Response: Данные о текущем пользователе.
        """
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionsView(APIView):
    """
    Представление для получения списка подписок пользователя.

    Позволяет получить список пользователей, на которых подписан
    текущий пользователь.

    Methods:
        - get(request): Получение списка подписок текущего пользователя.
    """
    def get(self, request):
        user = request.user
        queryset = User.objects.filter(subscriber__subscriber=user)
        serializer = UserSubscriptionSerializer(queryset, many=True,
                                                context={'request': request})
        return Response(serializer.data)
