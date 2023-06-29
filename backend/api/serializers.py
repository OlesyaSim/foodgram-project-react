from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Cart, FavoritesRecipes, Ingredients, Product,
                            Recipe, Tag)
from users.serializers import Base64ImageField, UserFoodgramSerializer

from .validators import ingredients_validate

User = get_user_model()


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


class RecipeSerializer(serializers.ModelSerializer):
    """ Выдача рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserFoodgramSerializer(read_only=True, many=False)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True, )
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
        return (
                user.is_authenticated and
                obj.in_favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.in_cart.filter(user=user).exists()

    def get_ingredients(self, obj):
        qs = Ingredients.objects.filter(recipe=obj)
        return IngredientsSerializer(qs, many=True).data


class ChangeIngredientsSerializer(serializers.ModelSerializer):
    """Модель связи ингредиента и рецепта. Включает в себя кол-во (сумму)
    ингредиента."""
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = Ingredients


class ChangeRecipeSerializer(serializers.ModelSerializer):
    """ Создание, изменение рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
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

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError('Время должно быть больше 0')
        return value

    def validate_tags_unique(self, value):
        return set(value)

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise ValidationError('Необходимо указать хотя бы один тэг')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def create(self, validate_data):
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        recipe_obj = Recipe.objects.create(
            author=self.context.get('request').user, **validate_data
        )
        list_ingredients = ingredients_validate(ingredients, recipe_obj)
        Ingredients.objects.bulk_create(list_ingredients)
        recipe_obj.tags.set(tags)
        return recipe_obj

    def update(self, obj, validate_data):
        obj.tags.clear()
        Ingredients.objects.filter(recipe=obj, ).delete()
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        list_ingredients = ingredients_validate(ingredients, obj)
        Ingredients.objects.bulk_create(list_ingredients)
        obj.tags.set(tags)
        return super().update(obj, validate_data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Получение данных для выдачи полноценного рецепта со всеми полями как
    указано в redoc."""
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
