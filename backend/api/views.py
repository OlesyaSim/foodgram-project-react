from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Cart, FavoritesRecipes, Ingredients, Product,
                            Recipe, Tag)
from users.serializers import RecipeOfSubscribersSerializer

from .filters import ProductSearchFilter, RecipesFilter
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CartSerializer, ChangeRecipeSerializer,
                          FavoritesRecipesSerializer, ProductSerializer,
                          RecipeSerializer, TagSerializer)
from .validators import list_shopping_filename

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None
    filter_backends = (ProductSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializer
        return ChangeRecipeSerializer

    @action(methods=['delete', 'post'], detail=True,
            url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exist_rel = Cart.objects.filter(recipe=recipe,
                                        user=user).first()
        if request.method == 'POST':
            if exist_rel:
                return Response(
                    {'detail': 'Рецепт уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Cart.objects.create(
                recipe=recipe,
                user=user
            )
            serializer = RecipeOfSubscribersSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not exist_rel:
                return Response({'detail': 'Такого рецепта нет в списке '
                                           'покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            exist_rel.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            url_path='download_shopping_cart', )
    def download_shopping_cart(self, request):
        user = self.request.user
        filename = list_shopping_filename(user)
        purchases = f'Список покупок {user.username}\n\n'
        shopping_dict = {}
        ingredients = Ingredients.objects.filter(
            recipe__in_cart__user=user).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        for num, i in enumerate(ingredients):
            name = i['ingredients__name']
            amount = i['amount']
            measur = i['ingredients__measurement_unit']
            if name not in shopping_dict:
                shopping_dict[name] = {
                    "amount": amount,
                    "measur": measur,
                }
            else:
                shopping_dict[name]["amount"] += amount
        purchases += "\n".join([f"{name} - {values['amount']}"
                                f"{values['measur']}"
                                for (name, values) in shopping_dict.items()])
        response = HttpResponse(purchases,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(methods=['delete', 'post'],
            detail=True,
            url_path='favorite',
            permission_classes=(IsAuthenticated,), )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exist_rel = FavoritesRecipes.objects.filter(recipe=recipe,
                                                    user=user).first()
        if request.method == 'POST':
            if exist_rel:
                return Response(
                    {'detail': 'Рецепт уже был ранее добавлен в Избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoritesRecipes.objects.create(
                recipe=recipe,
                user=user
            )
            serializer = RecipeOfSubscribersSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not exist_rel:
                return Response({'detail': 'Ошибка удаления рецепта из '
                                           'избранного'},
                                status=status.HTTP_400_BAD_REQUEST)
            exist_rel.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritesRecipesViewSet(viewsets.ModelViewSet):
    queryset = FavoritesRecipes.objects.all()
    serializer_class = FavoritesRecipesSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
