from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка является ли юзер автором с правом редактировать,
    если нет - только чтение контента."""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
                request.method in permissions.SAFE_METHODS
                or obj.author == request.user
        )


class ReadOnly(permissions.BasePermission):
    """Право только на чтение контента."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
