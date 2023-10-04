from rest_framework.routers import DefaultRouter
from django.urls import path, include

from api.v1.views import CustomUserViewSet, SubscriptionViewSet, TagsViewSet, \
    RecipesViewSet, IngredientsViewSet

router = DefaultRouter()

router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipesViewSet)
router.register(r'tags', TagsViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'users/subscriptions', SubscriptionViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),

    ]
