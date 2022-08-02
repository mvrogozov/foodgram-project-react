from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from .views import IngredientViewSet, TagViewSet, RecipeViewSet, UserViewSet
from .views import MyTokenObtainPairView


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)


urlpatterns = [
    path('', include(router.urls), name='api_tag_list'),
    path('auth/', include('djoser.urls.authtoken')),
]

#path('auth/token/login/', MyTokenObtainPairView.as_view(), name='login' )