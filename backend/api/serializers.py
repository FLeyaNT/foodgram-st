from djoser.serializers import UserCreateSerializer

from django.contrib.auth import (
    get_user_model,
    password_validation
)
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from rest_framework import serializers

from typing import Union

from ingredients.models import Ingredient
from recipes.models import (
    RecipeIngredient, Recipe, Favorites,
    ShoppingCart
)
from users.models import Follower

from .serializers import (
    CustomUserSerializer,
)

from utils.base64field import Base64ImageField


User = get_user_model()


# ===========================================================
#                       Ingredients
# ===========================================================


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


# ===========================================================
#                       Recipes
# ===========================================================


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте"""

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError({
                'detail': 'Количество не может быть меньше единицы.'
            })
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""

    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_through'
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text',
            'cooking_time'
        )
        read_only_fields = ('id',)

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )
        return value

    def add_ingredients(self, recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(
                Ingredient,
                pk=ingredient['ingredient']['id']
            )
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=ingredient['amount']
                )
            )

        if len(ingredients_list) == 0:
            raise serializers.ValidationError({
                'detail': 'Список ингредиентов не может быть пустым'
            })

        RecipeIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data: dict):
        ingredients = validated_data.pop('recipe_through')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data: dict):
        ingredients = validated_data.pop('recipe_through', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients is not None:
            instance.recipe_through.all().delete()
            self.add_ingredients(instance, ingredients)

        return instance

    def get_is_favorited(self, obj: Recipe):
        return self.is_recipe_added(obj, Favorites)

    def get_is_in_shopping_cart(self, obj: Recipe):
        return self.is_recipe_added(obj, ShoppingCart)

    def is_recipe_added(
        self,
        obj: Recipe,
        klass: Union[Favorites, ShoppingCart]
    ):
        request: HttpRequest = self.context.get('request')
        if request.user.is_authenticated:
            return klass.objects.filter(
                recipe=obj,
                user=request.user
            ).exists()
        return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода рецепта, добавленного в избранное
    или корзину покупок
    """

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time'
        )


# ===========================================================
#                       Users
# ===========================================================


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастоиного пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        current_user = request.user
        return Follower.objects.filter(
            subscriber=current_user,
            subscribed=obj
        ).exists()


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для для подписки на пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        return ShortRecipeSerializer(
            obj.recipes.all(),
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя"""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""

    current_password = serializers.CharField(
        required=True, write_only=True
    )
    new_password = serializers.CharField(
        required=True, write_only=True
    )

    def validate_current_password(self, value):
        request = self.context.get('request')
        user = request.user
        if isinstance(user, User):
            if not user.check_password(value):
                raise serializers.ValidationError({
                    'detail': 'Неверный текущий пароль'
                })
        return value

    def validate(self, attrs: dict):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        user = self.context['request'].user

        if current_password == new_password:
            raise serializers.ValidationError({
                'detail': 'Новый пароль совпадает со старым'
            })

        password_validation.validate_password(
            password=new_password,
            user=user
        )

        return attrs
