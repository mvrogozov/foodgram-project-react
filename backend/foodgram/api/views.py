from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .api_permissions import IsAuthorOrReadOnly
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User
from recipes.models import Favorite, Follow, Tag, Recipe, Ingredient
from recipes.models import ShoppingCart
from .serializers import SubscriptionSerializer, TagSerializer
from .serializers import PasswordSerializer, UserPostSerializer
from .serializers import ShortRecipeSerializer, UserSerializer
from .serializers import RecipePostSerializer, IngredientSerializer
from .serializers import RecipeSerializer
from django.http import FileResponse
from .mixins import mymix

from .utils import create_pdf


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(
            user=self.request.user
            ).select_related('author')
        return queryset

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        serializer.save(author=author, user=self.request.user)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPostSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
        )
    def subscriptions(self, request):
        user = get_object_or_404(User, username=request.user.username)
        queryset = user.follower.all().annotate(
            recipes_count=Count('author__recipes')
        )
        serializer = SubscriptionSerializer(many=True, instance=queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
        )
    def subscribe(self, request, pk=None):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, pk=pk)
        following, _ = Follow.objects.get_or_create(user=user, author=author)
        if request.method == 'POST':
            following = Follow.objects.filter(
                user=user, author=author
                ).annotate(recipes_count=Count('author__recipes'))
            serializer = SubscriptionSerializer(instance=following, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following.delete()
        return Response('Отписка выполнена', status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(
            serializer.validated_data.get('current_password')
        ):
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response('wrong password', status=status.HTTP_401_UNAUTHORIZED)


class RecipeViewSet(ModelViewSet, mymix):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_fields = ('name', 'tags')
    search_fields = ('name', 'tags__slug')
    ordering_fields = ('name', 'cooking_time')
    ordering = ('name',)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            print('get post ser')
            return RecipePostSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            self.permission_classes = [IsAuthorOrReadOnly, ]
        return super(RecipeViewSet, self).get_permissions()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
        )
    def shopping_cart(self, request, pk=None):
        return mymix.create_delete_record(
            self,
            request,
            pair_model=Recipe,
            user_model=User,
            through_model=ShoppingCart,
            pair_field='recipe',
            serializer=ShortRecipeSerializer,
            exist_message='Уже в корзине',
            pk=pk
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return mymix.create_delete_record(
            self,
            request,
            pair_model=Recipe,
            user_model=User,
            through_model=Favorite,
            pair_field='recipe',
            serializer=ShortRecipeSerializer,
            exist_message='Уже в избранном',
            pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = get_object_or_404(User, username=request.user)
        cart = Recipe.objects.filter(shopping_cart__user=user)
        shopping_list = {}
        for recipe in cart:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                ingredient_for_recipe = ingredient.for_recipe.get(
                    recipe=recipe
                )
                shopping_list.setdefault(ingredient.name, [0, ''])
                shopping_list[ingredient.name][0] += (
                    ingredient_for_recipe.amount
                )
                shopping_list[ingredient.name][1] = ingredient.measurement_unit

        buffer = create_pdf(shopping_list)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping list.pdf'
        )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
