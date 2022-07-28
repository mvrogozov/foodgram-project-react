import os
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from users.models import User
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart
from .serializers import TagSerializer, RecipeSerializer, IngerdientSerializer
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings



class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, pk=None):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            serializer = self.serializer_class(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get']
    )
    def download_shopping_cart(self, request):
        user = get_object_or_404(User, username=request.user)
        print('user= ', user.username, '\n')
        cart = Recipe.objects.filter(shopping_cart__user=user)
        shopping_list = {}
        for recipe in cart:
            ingredients = recipe.ingredients.all()
            print('ingredients= ', ingredients, '\n')
            for ingredient in ingredients:
                ingredient_for_recipe = ingredient.for_recipe.get(recipe=recipe)
                shopping_list.setdefault(ingredient.name, 0)
                shopping_list[ingredient.name] += ingredient_for_recipe.amount
                print('ingredient= ', ingredient, 'amount=', ingredient_for_recipe.amount)
            print('list=', shopping_list, '\n')

        buffer = io.BytesIO()
        pdf_object = canvas.Canvas(buffer, pagesize='A4')
        #pdfmetrics.registerFont(TTFont('Mariupol-Regular', os.path.join(settings.TEMPLATES_DIR, 'Mariupol-Regular.ttf'), 'UTF-8'))
        pdfmetrics.registerFont(TTFont('Mariupol-Regular', 'Mariupol-Regular.ttf', 'UTF-8'))
        pdf_object.setFont('Mariupol-Regular', 12)
        x = 10
        y = 730
        for item, amount in shopping_list.items():
            pdf_object.drawString(x, y, item + ': ' + str(amount))
            y -= 20
        pdf_object.drawString(x, y, 'TEST string test STRING 123456789')
        pdf_object.showPage()
        pdf_object.save()
        print(pdf_object)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shopping list.pdf')


        #serializer = self.serializer_class(instance=cart[0])
        #return Response(serializer.data, status=status.HTTP_200_OK)



class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngerdientSerializer
