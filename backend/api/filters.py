from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class ProductSearchFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, qs, name, value):
        if value:
            return qs.filter(in_favorites__user=self.request.user)
        return qs

    def filter_is_in_shopping_cart(self, qs, name, value):
        if value:
            return qs.filter(in_cart__user=self.request.user)
        return qs
