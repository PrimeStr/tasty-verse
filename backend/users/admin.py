from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели User.

    Attributes:
        list_display (tuple): Список полей, отображаемых
        в списке пользователей.
        list_filter (tuple): Список полей, по которым можно
        фильтровать пользователей.
        search_fields (tuple): Список полей, по которым можно
        выполнять поиск пользователей.
        ordering (tuple): Поле(-я), по которому(-ым) сортируется
        список пользователей.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Subscription.

    Attributes:
        list_display (tuple): Список полей, отображаемых в списке подписок.
        list_filter (tuple): Список полей, по которым можно
        фильтровать подписки.
        search_fields (tuple): Список полей, по которым можно
        выполнять поиск подписок.
        ordering (tuple): Поле(-я), по которому(-ым) сортируется
        список подписок.
    """
    list_display = ('subscriber', 'target_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__username', 'target_user__username')
    ordering = ('-created_at',)
