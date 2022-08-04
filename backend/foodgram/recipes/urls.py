from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndexView, RecipeDetailView

app_name = 'recipes'


urlpatterns = [
    path('', IndexView.as_view(), name='recipes_index'),
    
    path(
        'recipes/<int:recipe_id>/',
        RecipeDetailView.as_view(),
        name='recipe_detail'
    ),
]
