from django_filters.rest_framework import filters, FilterSet

from ingredients.models import Ingredient
from recipes.models import Recipe


# ===========================================================
#                       Ingredients
# ===========================================================


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов"""

    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


# ===========================================================
#                       Recipes
# ===========================================================


class RecipeFilter(FilterSet):
    """Фильтры для модели Recipe"""

    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
