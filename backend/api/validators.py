from rest_framework import serializers

from recipes.models import Ingredients


def ingredients_validate(ingredients, recipe_obj):
    list_ingredients = []
    for ingredient in ingredients:
        for ingr_list in list_ingredients:
            if ingredient.get('id') == ingr_list:
                raise serializers.ValidationError({
                    "detail": "Такой ингредиент уже есть в рецепте."
                })
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    {"detail": "Количество не может быть меньше 1."})
        list_ingredients.append(Ingredients(recipe=recipe_obj,
                                            ingredients=ingredient.get('id'),
                                            amount=ingredient.get('amount')))
    return list_ingredients


def list_shopping_filename(user_obj):
    return f'{user_obj.username}_shopping_list.txt'
