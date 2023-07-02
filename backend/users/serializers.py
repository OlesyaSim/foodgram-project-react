import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.pagination import RecipeSubscribePagination
from recipes.models import Recipe

from .models import Subscriptions

User = get_user_model()


class UserFoodgramSerializer(serializers.ModelSerializer):
    """Выдача пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('username',
                  'id',
                  'email',
                  'first_name',
                  'last_name',
                  'is_subscribed',)
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and Subscriptions.objects.filter(
            user=user, author=obj).exists())


class UserCreateSerializer(serializers.ModelSerializer):
    """Изменение пользователя. Валидация в моделе."""

    class Meta:
        fields = ('username',
                  'password',
                  'id',
                  'email',
                  'first_name',
                  'last_name')
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        value = value.lower()
        if value == 'me':
            raise ValidationError(
                'Нельзя использовать это имя, выберите другое'
            )
        if User.objects.filter(username=value).exists():
            raise ValidationError("Такое имя уже зарегистрировано")
        return value

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise ValidationError("Такой email уже зарегистрирован")
        return value


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Подписчики."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',
                  )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and Subscriptions.objects.filter(
            user=user, author=obj).exists())

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj,)
        recipes = recipes[:int(RecipeSubscribePagination.page_size)]
        return RecipeOfSubscribersSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
        return super(UserTokenCreateSerializer, self).validate(attrs)


class RecipeOfSubscribersSerializer(serializers.ModelSerializer):
    """ Рецепты подписчиков. Рецепты в избранном подписчиков. Рецепты в списке
    покупок подписчиков."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        model = Recipe
