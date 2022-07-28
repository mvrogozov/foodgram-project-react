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
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('name', 'ingredients')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Ingredient_for_recipe)
admin.site.register([Favorite, Follow, ShoppingCart])
