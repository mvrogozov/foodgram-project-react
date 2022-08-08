from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, TagViewSet, RecipeViewSet, UserViewSet


router = DefaultRouter()
router.register('tags', TagViewSet, basename='api_tags')
router.register('recipes', RecipeViewSet, basename='api_recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='api_users')

urlpatterns = [
    path('', include(router.urls), name='api_tag_list'),
    path('auth/', include('djoser.urls.authtoken')),
]
