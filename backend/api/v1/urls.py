from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.views import (TagsAPIView, RecipesAPIView, IngredientsAPIView,
                          FavoritesAPIView, ShoppingCartAPIView,
                          RecipesDetailAPIView)
from users.views import CustomUserViewSet

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
#router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('tags/', TagsAPIView.as_view(), name='tags'),
    path('tags/<int:pk>/', TagsAPIView.as_view(), name='tags-detail'),
    path('recipes/', RecipesAPIView.as_view(), name='recipes'),
    path('recipes/<int:pk>/', RecipesDetailAPIView.as_view(), name='recipe-detail'),
    path('ingredients/', IngredientsAPIView.as_view(), name='ingredients'),
    path('ingredients/<int:pk>/', IngredientsAPIView.as_view(), name='ingredients'),
    path('recipes/<int:pk>/favorite/', FavoritesAPIView.as_view(), name='favorite'),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartAPIView.as_view(), name='shopping_cart'),
]
