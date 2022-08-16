from django_filters import rest_framework as rf_filters
from recipes.models import Recipe
from rest_framework import filters
from users.models import User


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class UserFilter(rf_filters.FilterSet):
    is_subscribed = rf_filters.BooleanFilter(method='filter_is_subscribed')

    def filter_is_subsrcibed(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(following__user=self.request.user)
        return queryset


class RecipeFilter(rf_filters.FilterSet):
    tags = rf_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
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
            return Recipe.objects.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
