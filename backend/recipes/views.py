from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Recipe, Favorites, ShoppingCart
from .serializers import (
    RecipeSerializer, ShortRecipeSerializer,
    RecipeIngredientSerializer
)
from .permissions import IsOwnerOrReadOnly

from utils.generate_pdf import generate_pdf


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )

    def get_queryset(self):
        queryset = Recipe.objects.all()
        request: HttpRequest = self.request
        user = request.user

        is_in_shopping_cart = request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = request.query_params.get(
            'is_favorited'
        )

        if is_in_shopping_cart and user.is_authenticated:
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    shopping_cart__user=user
                )
        
        if is_favorited and user.is_authenticated:
            if is_favorited == '1':
                queryset = queryset.filter(
                    favorites__user=user
                )
        
        return queryset


    def perform_create(self, serializer: RecipeSerializer):
        serializer.save(author=self.request.user)


class RecipeLinkAPIView(APIView):
    """APIView для получения короткой ссылки на рецепт"""

    permission_classes = (permissions.AllowAny,)

    def get(self, request: HttpRequest, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=kwargs['id']
        )
        new_url = request.build_absolute_uri(f'/s/{recipe.short_code}')
        return Response(
            {
                'short-link': new_url
            },
            status=status.HTTP_200_OK
        )
        

class RecipeByShortLinkAPIView(APIView):
    """
    APIView для получения определенного рецепта по его
    короткой ссылке
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request: HttpRequest, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            short_code=kwargs['code']
        )
        return redirect(f'/recipes/{recipe.pk}/')


class AddToFavoriteAPIView(APIView):
    """
    APIView для добавления рецепта в избранное и
    его удаления из избранного
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        recipe = self.get_recipe(**kwargs)
        current_user = request.user

        favorite_exists = Favorites.objects.filter(
            recipe=recipe,
            user=current_user
        ).exists()

        if favorite_exists:
            return Response(
                data={
                    'data': 'Рецепт уже есть в избранном'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorites.objects.create(
            recipe=recipe,
            user=current_user
        )
        serializer = ShortRecipeSerializer(
            recipe
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request: HttpRequest, *args, **kwargs):
        recipe = self.get_recipe(**kwargs)
        current_user = request.user

        favorite = Favorites.objects.filter(
            recipe=recipe,
            user=current_user
        ).first()

        if not favorite:
            return Response(
                data={
                    'data': 'Рецепта нет в избранном'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        favorite.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def get_recipe(self, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=kwargs['id']
        )
        return recipe
    

class AddToShoppingCartAPIView(APIView):

    def post(self, request: HttpRequest, *args, **kwargs):
        recipe = self.get_recipe(**kwargs)
        current_user = request.user

        is_in_shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe,
            user=current_user
        ).exists()

        if is_in_shopping_cart:
            return Response(
                data={
                    'data': 'Рецепт уже в списке покупок'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ShoppingCart.objects.create(
            recipe=recipe,
            user=current_user
        )

        serializer = ShortRecipeSerializer(
            recipe
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request: HttpRequest, *args, **kwargs):
        recipe = self.get_recipe(**kwargs)
        current_user = request.user

        favorite = ShoppingCart.objects.filter(
            recipe=recipe,
            user=current_user
        ).first()

        if not favorite:
            return Response(
                data={
                    'data': 'Рецепта нет в избранном'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        favorite.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def get_recipe(self, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=kwargs['id']
        )
        return recipe


class DownloadPDFAPIView(APIView):
    """APIView для скачивания PDF файла со списком продуктов"""

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        ingredients = Recipe.objects.filter(
            shopping_cart__user=user
        ).values(
            'recipe_through__ingredient__name',
            'recipe_through__ingredient__measurement_unit',
            'recipe_through__amount'
        )
        
        pdf_content = generate_pdf(ingredients)

        response = HttpResponse(
            pdf_content, 
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping-list.pdf"'
        return response
