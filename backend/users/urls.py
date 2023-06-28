from rest_framework.routers import DefaultRouter

from .views import SubscriptionsViewSet, UserFoodgramViewSet
from django.urls import path, include

v1_router_users = DefaultRouter()

v1_router_users.register('users', UserFoodgramViewSet, basename='users')
v1_router_users.register(
    'subscriptions', SubscriptionsViewSet, basename='subscriptions'
)
urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router_users.urls)),
]
