from django.contrib import admin

from .models import Ingredients, Product, Recipe, Tag


class IngredientsInline(admin.TabularInline):
    model = Ingredients


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name')


@admin.register(Recipe)
class ResipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'count_recipes')
    search_fields = ('name', 'tags', 'author')
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('name',)
    inlines = (IngredientsInline,)

    @staticmethod
    def count_recipes(obj):
        return obj.in_favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
