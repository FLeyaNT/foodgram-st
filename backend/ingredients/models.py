from django.db import models


class Ingredient(models.Model):
    """Модель описывающая ингредиент"""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=128,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Мера',
        max_length=64
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
