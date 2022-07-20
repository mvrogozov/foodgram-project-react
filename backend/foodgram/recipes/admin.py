from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Ingredient_for_recipe


class IngredientsInline(admin.TabularInline):
    model = Ingredient_for_recipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInline,)
    list_display = (
        'recipe_name',
        'author',
        'picture',
        'text_description',
        'cooking_time'
    )
    search_fields = ('recipe_name', 'ingredients')
    list_filter = ('recipe_name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Ingredient_for_recipe)
