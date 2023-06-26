from django.contrib import admin

from .models import Subscriptions, UserFoodgram


@admin.register(UserFoodgram)
class UserFoodgramAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'count_recipes',
        'count_subs',
        'last_name',
        'first_name')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')

    @staticmethod
    def count_recipes(obj):
        return obj.recipes.count()

    @staticmethod
    def count_subs(obj):
        return obj.subscriptions.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    search_fields = ('author', 'user')
    list_filter = ('author', 'user')
