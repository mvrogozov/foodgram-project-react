from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientForRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientsInline(admin.TabularInline):
    model = IngredientForRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInline,)
    list_display = (
        'name',
        'author',
    )
    list_filter = ('name', 'author', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientForRecipe)
admin.site.register([Favorite, Follow, ShoppingCart])
