from django_filters.rest_framework import DjangoFilterBackend

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet

from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import IngredientFilter
from .serializers import IngredientSerializer, CustomUserSerializer

from ingredients.models import Ingredient
from recipes.models import Recipe
from users.models import Follower

from .serializers import (
    RecipeSerializer, ShortRecipeSerializer,
    FollowSerializer, AvatarSerializer,
    ChangePasswordSerializer
)
from .permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter

from utils.generate_pdf import generate_pdf


User = get_user_model()


# ===========================================================
#                       Ingredients
# ===========================================================


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


# ===========================================================
#                       Recipes
# ===========================================================


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = (
        Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'ingredients'
        )
    )
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer: RecipeSerializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('get',),
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',
        queryset=Recipe.objects.all()
    )
    def get_recipe_link(self, request: HttpRequest, pk=None):
        """Метод для получения короткой ссылки на рецепт"""
        recipe = self.get_object()
        new_url = request.build_absolute_uri(f'/s/{recipe.short_code}')
        return Response(
            data={'short-link': new_url},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,),
        queryset=Recipe.objects.all()
    )
    def favorite_method(self, request: HttpRequest, pk=None):
        """Метод для добавления и удаления рецепта из избранного"""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if recipe.in_featured.filter(id=user.id).exists():
                return Response(
                    data={'data': 'Рецепт уже есть в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.in_featured.add(request.user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            if not recipe.in_featured.filter(id=user.id).exists():
                return Response(
                    data={'data': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.in_featured.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        queryset=Recipe.objects.all(),
    )
    def shopping_cart_method(self, request: HttpRequest, pk=None):
        """Метод для добавления и удаления рецепта из корзины покупок"""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if recipe.in_shopping_cart.filter(id=user.id).exists():
                return Response(
                    data={'data': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.in_shopping_cart.add(user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            if not recipe.in_shopping_cart.filter(id=user.id).exists():
                return Response(
                    data={'data': 'Рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.in_shopping_cart.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request: HttpRequest):
        """Метод для генерации pdf файла со списком покупок"""
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
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.pdf"'
        )
        return response


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


# ===========================================================
#                       Users
# ===========================================================


class CustomUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request: HttpRequest):
        serializer = self.get_serializer(request.user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def follow(self, request: HttpRequest, id=None):
        """Метод для подписки и отписки от пользователя"""
        user_to_follow = self.get_object()
        user = request.user

        follow = Follower.objects.filter(
            subscriber=user,
            subscribed=user_to_follow
        ).first()

        if request.method == 'POST':
            if (
                user == user_to_follow
                or follow
            ):
                return Response(
                    data={'detail': 'Ошибка подписки'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follower.objects.create(
                subscriber=user,
                subscribed=user_to_follow
            )
            serializer = FollowSerializer(
                user_to_follow,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            if not follow:
                return Response(
                    data={'detail': 'Ошибка отписки'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            follow.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def followers_list(self, request: HttpRequest):
        """Метод для вывода всех подписок пользователя"""
        user = request.user
        queryset = User.objects.filter(
            subscribers__subscriber=user
        )
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request: HttpRequest):
        """Метод для изменения и удаления аватара"""
        user = request.user
        user.avatar.delete(save=False)

        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            user.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('post',),
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def change_password(self, request: HttpRequest):
        """Метод для смены пароля пользователя"""
        user = request.user
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user.set_password(
                serializer.validated_data.get('new_password')
            )
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
