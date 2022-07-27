from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from recipes.models import Recipe


class IndexView(ListView):

    model = Recipe
    paginate_by = 10  # settings.RECIPES_AMOUNT
    template_name = 'recipes/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        title = 'Главная страница'
        context.update({
            'title': title
        })
        return context


class RecipeDetailView(ListView):
    template_name = 'recipes/recipe_detail.html'

    def get_queryset(self):
        self.recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        return self.recipe

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        title = self.recipe.name
        context.update({
            'recipe': self.recipe,
            'title': title
        })
        return context






