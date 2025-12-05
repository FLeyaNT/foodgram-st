from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from .models import (
    RecipeIngredient, Recipe, Favorites,
    ShoppingCart
)
from ingredients.models import Ingredient
from utils.base64field import Base64ImageField
from users.serializers import CustomUserSerializer

from typing import Union


User = get_user_model()


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
            raise serializers.ValidationError(
                'Количество не может быть меньше единицы.'
            )
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
