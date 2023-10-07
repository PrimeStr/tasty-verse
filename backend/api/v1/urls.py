from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.views import (CustomUserViewSet, TagsAPIView,
                          RecipesAPIView, IngredientsAPIView,
                          FavoritesAPIView, ShoppingCartAPIView)

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('tags/', TagsAPIView.as_view(), name='tags'),
    path('recipes/', RecipesAPIView.as_view(), name='recipes'),
    path('ingredients/', IngredientsAPIView.as_view(), name='ingredients'),
    path('recipes/<int:pk>/favorite/', FavoritesAPIView.as_view(), name='favorite'),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartAPIView.as_view(), name='shopping_cart'),
]
