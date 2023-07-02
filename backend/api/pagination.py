from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6

class RecipeSubscribePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 3
