from django.contrib import admin

from .models import (
    Recipe, RecipeIngredient,
    ShoppingCart, Favorites
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author')
    readonly_fields = ('favorites_count', 'short_code')
    autocomplete_fields = ('author',)
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное"""
        
        return obj.in_featured.count()
    favorites_count.short_description = "В избранном"


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')
