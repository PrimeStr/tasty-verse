from django.contrib import admin

from .models import User, Subscription

admin.site.register(User)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'target_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__username', 'target_user__username')
