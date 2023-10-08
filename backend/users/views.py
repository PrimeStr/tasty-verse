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
    """"""
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
        """"""
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
        """"""
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
            serializer = UserSubscriptionSerializer(target_user,
                                                    context={'request': request})
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
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionsView(APIView):
    def get(self, request):
        user = request.user
        queryset = User.objects.filter(subscriber__subscriber=user)
        serializer = UserSubscriptionSerializer(queryset, many=True,
                                                context={'request': request})
        return Response(serializer.data)
