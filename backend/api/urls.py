from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CartViewSet,
    FavoritesRecipesViewSet,
    ProductViewSet,
    RecipeViewSet,
    TagViewSet,
)

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('cart',
                   CartViewSet, basename='cart'
                   )
v1_router.register('favorite',
                   FavoritesRecipesViewSet, basename='favorite'
                   )
v1_router.register('ingredients', ProductViewSet, basename='ingredients')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('users.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
