from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Follow, Ingredient, IngredientForRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User

from .api_permissions import IsAuthorOrReadOnly
from .mixins import CreateDeleteRecordMixin
from .serializers import (IngredientSerializer, PasswordSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscriptionSerializer,
                          TagSerializer, UserPostSerializer, UserSerializer)
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
        return Response('Отписка выполнена', status=status.HTTP_204_NO_CONTENT)

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
    filterset_fields = ('name', 'tags')
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
        permission_classes=[IsAuthenticated]
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
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).values_list('id', flat=True)
        shopping_list = {}
        ingredients_for_all = IngredientForRecipe.objects.filter(
            recipe__in=cart
        ).annotate(total=Sum('amount', distinct=True)).order_by(
            'ingredient_name'
        )
        for ingredient in ingredients_for_all:
            shopping_list.setdefault(ingredient.ingredient_name, [0, ''])
            shopping_list[ingredient.ingredient_name][0] = ingredient.total
            shopping_list[ingredient.ingredient_name][1] = (
                ingredient.ingredient_name.measurement_unit
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None
