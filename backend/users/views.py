from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscriptions
from .serializers import SubscriptionsSerializer, UserFoodgramSerializer

User = get_user_model()


class UserFoodgramViewSet(UserViewSet):
    serializer_class = UserFoodgramSerializer

    @action(methods=['get'],
            detail=False,
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,),
            )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscribers__user=self.request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['delete', 'post'],
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscribe_obj, created = Subscriptions.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return Response(
                    {'detail': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscriptionsSerializer(subscribe_obj.author,
                                                 context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            subscribe_obj = Subscriptions.objects.filter(user=user,
                                                         author=author)
            if not subscribe_obj.exists():
                return Response({'detail': 'Ошибка отписки. Сначала нужно '
                                           'подписаться.'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionsSerializer
    pagination_class = PageNumberPagination
