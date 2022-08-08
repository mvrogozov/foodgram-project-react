from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Ingredient_for_recipe, Follow
from .models import Favorite, ShoppingCart


class IngredientsInline(admin.TabularInline):
    model = Ingredient_for_recipe
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
admin.site.register(Ingredient_for_recipe)
admin.site.register([Favorite, Follow, ShoppingCart])
