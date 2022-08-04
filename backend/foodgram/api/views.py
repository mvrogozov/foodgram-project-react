import os
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User
from recipes.models import Favorite, Follow, Tag, Recipe, Ingredient, ShoppingCart
from .serializers import SubscriptionSerializer, TagSerializer, RecipeSerializer, IngredientSerializer
from .serializers import PasswordSerializer, UserPostSerializer
from .serializers import ShortRecipeSerializer, UserSerializer
from .serializers import RecipePostSerializer
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import mm, inch
from reportlab.platypus import PageBreak
from django.conf import settings
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SubscriptionViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPostSerializer
        print('\n get')
        return SubscriptionSerializer

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        print('\n in get')
        user = get_object_or_404(User, username=request.user.username)
        queryset = user.following.all()
        print('\n queryset = ', queryset)
        return Response('okk')

    @action(detail=True, methods=['post', 'delete'])
    def subscriptions(self, request, pk=None):
        print('\n here')
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, pk=pk)
        following, _ = Follow.objects.get_or_create(user=user, author=author)
        if request.method == 'POST':
            return Response('Подписка выполнена', status=status.HTTP_201_CREATED)
        following.delete()
        return Response('Отписка выполнена', status=status.HTTP_204_NO_CONTENT)



class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPostSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data.get('current_password')):
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response('wrong password', status=status.HTTP_401_UNAUTHORIZED)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, pk=None):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response('Уже в корзине', status=status.HTTP_400_BAD_REQUEST)
            cart = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Уже в избранном', status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(
        detail=False,
        methods=['get']
    )
    def download_shopping_cart(self, request):
        user = get_object_or_404(User, username=request.user)
        cart = Recipe.objects.filter(shopping_cart__user=user)
        shopping_list = {}
        for recipe in cart:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                ingredient_for_recipe = ingredient.for_recipe.get(recipe=recipe)
                shopping_list.setdefault(ingredient.name, [0, ''])
                shopping_list[ingredient.name][0] += ingredient_for_recipe.amount
                shopping_list[ingredient.name][1] = ingredient.measurement_unit

        FONT_SIZE = 12
        A4_WIDTH = 210 * mm
        A4_HEIGHT = 297 * mm
        buffer = io.BytesIO()
        pdf_object = canvas.Canvas(buffer, pagesize='A4')
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(settings.TEMPLATES_DIR, 'arial.ttf'), 'UTF-8'))
        pdf_object.setFillColorRGB(0.2, 0.2, 0.9)
        x = 20
        y = A4_HEIGHT - 150
        pdf_object.setFont('Arial', FONT_SIZE + 4)
        pdf_object.drawString(x + 200, y + 50, 'Список покупок.')
        pdf_object.setFont('Arial', FONT_SIZE)
        for item, amount in shopping_list.items():
            #pdf_object.drawString(x, y, item + ': ' + str(amount[0]) + amount[1])
            pdf_object.drawString(x, y, f'{item}: {str(amount[0])} {amount[1]}')
            y -= 20
            if y < 30:
                pdf_object.showPage()
                pdf_object._pageNumber += 1
                pdf_object.setFont('Arial', FONT_SIZE)
                pdf_object.setFillColorRGB(0.2, 0.2, 0.7)
                y = A4_HEIGHT - 10
        pdf_object.drawString(x, y, '_________________________________________')
        pdf_object.showPage()
        pdf_object.save()
        print(pdf_object)
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping list.pdf'
        )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
