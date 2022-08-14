from django_filters import rest_framework as rf_filters
from recipes.models import Recipe


class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ['tags', ]
