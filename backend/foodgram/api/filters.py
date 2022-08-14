from django_filters import rest_framework as rf_filters
from recipes.models import Recipe
from rest_framework import filters


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'ingredient_name'



class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ['tags', ]
