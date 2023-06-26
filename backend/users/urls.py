from rest_framework.routers import DefaultRouter

from .views import SubscriptionsViewSet, UserFoodgramViewSet

v1_router_users = DefaultRouter()

v1_router_users.register('users', UserFoodgramViewSet, basename='users')
v1_router_users.register(
    'subscriptions', SubscriptionsViewSet, basename='subscriptions'
)
