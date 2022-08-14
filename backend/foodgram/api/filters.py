from django_filters import rest_framework as rf_filters
from recipes.models import Recipe
from rest_framework import filters
from users.models import User


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'ingredient_name'


class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = rf_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags', ]
