from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import permissions

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для ингредиентов"""

    serializer_class = IngredientSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    pagination_class = None

    def get_queryset(self):
        queryset = None
        name = self.request.query_params.get('name')
        if name:
            queryset = Ingredient.objects.filter(
                name__istartswith=name
            )
        return queryset
