from django_filters import rest_framework as rf_filters
from recipes.models import Recipe


class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.CharFilter(field_name='tags__tag_name')

    class Meta:
        model = Recipe
        fields = ['tags', ]
