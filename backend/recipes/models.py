import shortuuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core import validators

from ingredients.models import Ingredient


User = get_user_model()


class Recipe(models.Model):
    """Модель для описания рецепта"""

    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Список ингредиентов'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        upload_to='recipes/images/'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[validators.MinValueValidator(1)]
    )
    short_code = models.CharField(
        max_length=3,
        blank=True,
        unique=True
    )
    in_featured = models.ManyToManyField(
        to=User,
        through='Favorites',
        related_name='favorite_recipes',
        verbose_name='Пользователи добавившие в избранное'
    )
    in_shopping_cart = models.ManyToManyField(
        to=User,
        through='ShoppingCart',
        related_name='recipes_in_shopping_cart',
        verbose_name='Пользователи, добавившие рецепт в корзину покупок'
    )

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortuuid.ShortUUID().random(length=3)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    """Модель для реализации корзины покупок"""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]


class Favorites(models.Model):
    """Модель для реализации избранного"""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]


class RecipeIngredient(models.Model):
    """Модель между рецептом и ингредиентом"""

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_through',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество в рецепте',
        validators=[validators.MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
