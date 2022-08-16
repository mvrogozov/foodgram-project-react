from django_filters import rest_framework as rf_filters
from recipes.models import Recipe
from rest_framework import filters
from users.models import User


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class IngredientFilter(rf_filters.FilterSet):
    pass


class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )
    author = rf_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = rf_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rf_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
