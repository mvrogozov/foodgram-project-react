from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Follow, Ingredient, IngredientForRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import User
from .api_permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientSearchFilter, UserFilter
from .mixins import CreateDeleteRecordMixin
from .serializers import (IngredientSerializer, PasswordSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscriptionSerializer,
                          TagSerializer, UserFollowSerializer,
                          UserPostSerializer, UserSerializer)
from .utils import create_pdf


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

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
        authors = request.user.follower.all().values_list('author', flat=True)
        queryset = User.objects.filter(pk__in=authors).annotate(
            recipes_count=Count('recipes')
        )
        pages = self.paginate_queryset(queryset)
        serializer = UserFollowSerializer(
            many=True,
            instance=pages,
            context={'request': request}
            )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
        )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        following, _ = Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
        if request.method == 'POST':
            following = Follow.objects.filter(
                user=request.user, author=author
                ).annotate(recipes_count=Count('author__recipes'))
            serializer = SubscriptionSerializer(instance=following, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following.delete()
        serializer = SubscriptionSerializer(instance=following, many=True)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.validate(request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(
            serializer.validated_data.get('current_password')
        ):
            request.user.set_password(
                serializer.validated_data.get('new_password')
            )
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response('wrong password', status=status.HTTP_401_UNAUTHORIZED)


class RecipeViewSet(ModelViewSet, CreateDeleteRecordMixin):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = RecipeFilter
    search_fields = ('name', 'tags__slug')
    ordering_fields = ('name', 'cooking_time')
    ordering = ('name',)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        pagination_class=None
        )
    def shopping_cart(self, request, pk=None):
        return self.create_delete_record(
            request=request,
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
        return self.create_delete_record(
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
        permission_classes=[IsAuthenticated],
        pagination_class=None
    )
    def download_shopping_cart(self, request):
        cart = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).values_list('id', flat=True)
        shopping_list = {}
        ingredients_for_all = IngredientForRecipe.objects.filter(
            recipe__in=cart
        ).values(
            'ingredient_name__name', 'ingredient_name__measurement_unit'
            ).annotate(total=Sum('amount', )).order_by(
            'ingredient_name'
        )
        for ingredient in ingredients_for_all:
            shopping_list.setdefault(
                ingredient['ingredient_name__name'], [0, '']
            )
            shopping_list[
                ingredient['ingredient_name__name']
                ][0] = ingredient['total']
            shopping_list[ingredient['ingredient_name__name']][1] = (
                ingredient['ingredient_name__measurement_unit']
            )
        buffer = create_pdf(shopping_list)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping list.pdf'
        )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, DjangoFilterBackend,)
    search_fields = ('^name',)
    filterset_fields = {
        'name': ['icontains']
    }
    pagination_class = None
