from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.permissions import IsAdminOrReadOnly
from users.models import Subscription, User
from users.serializers import UserSerializer, UserSubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    """"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    link_model = Subscription

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=PageNumberPagination,
    )
    def subscriptions(self,
                      request):  # ValueError: Cannot query "primestr": Must be "Subscription" instance.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
            return Response('Подписка оформлена',
                            status=status.HTTP_204_NO_CONTENT)

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



class UserSubscriptionsView(APIView):
    def get(self, request):
        user = request.user
        queryset = User.objects.filter(subscriber__subscriber=user)
        serializer = UserSubscriptionSerializer(queryset, many=True,
                                                context={'request': request})
        return Response(serializer.data)
