import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (
    Cart,
    FavoritesRecipes,
    Ingredients,
    Product,
    Recipe,
    Tag,
)
from users.models import Subscriptions


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
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Изменение пользователя."""
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
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj, )
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeOfSubscribersSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Тэги."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class ProductSerializer(serializers.ModelSerializer):
    """Продукт, который попадая в рецепт становится ингредиентом."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Product


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """ Выдача рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserFoodgramSerializer(read_only=True, many=False)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.in_favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.in_cart.filter(user=user).exists()

    def get_ingredients(self, obj):
        qs = Ingredients.objects.filter(recipe=obj)
        return IngredientsSerializer(qs, many=True).data


class RecipeOfSubscribersSerializer(serializers.ModelSerializer):
    """ Рецепты подписчиков. Рецепты в избранном. Рецепты в списке покупок."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',
                  )
        model = Recipe


class ChangeIngredientsSerializer(serializers.ModelSerializer):
    """Модель связи ингредиента и рецепта. Включает в себя кол-во (сумму)
    ингредиента."""
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = Ingredients


class ChangeRecipeSerializer(serializers.ModelSerializer):
    """ Создание, изменение рецептов."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = ChangeIngredientsSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance,
            context=context).data

    def create(self, validate_data):
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        recipe_obj = Recipe.objects.create(author=self.context.get(
            'request').user, **validate_data)
        for ingredient in ingredients:
            Ingredients.objects.create(recipe=recipe_obj,
                                       ingredients=ingredient.get('id'),
                                       amount=ingredient.get('amount'))
        for tag in tags:
            recipe_obj.tags.add(tag)
        return recipe_obj

    def update(self, obj, validate_data):
        obj.tags.clear()
        Ingredients.objects.filter(recipe=obj, ).delete()
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        for ingredient in ingredients:
            Ingredients.objects.create(recipe=obj,
                                       ingredients=ingredient.get('id'),
                                       amount=ingredient.get('amount'))
        for tag in tags:
            obj.tags.add(tag)
        return super().update(obj, validate_data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Ингридиенты с суммой из рецепта."""
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Ingredients

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit


class FavoritesRecipesSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""
    class Meta:
        fields = ('recipe', 'user', 'date_added')
        model = FavoritesRecipes


class CartSerializer(serializers.ModelSerializer):
    """Рецепты в списке покупок."""

    class Meta:
        fields = ('recipe', 'user', 'date_added')
        model = Cart
