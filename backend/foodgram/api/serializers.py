import base64
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Tag
from django.core.files.base import ContentFile


class Base64ImageField(serializers.Field):

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            # convert 64 to image

            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        except ValueError:
            raise serializers.ValidationError('wrong image')
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'author',
            'text',
            'ingredients',
            'cooking_time',
            'image',
            'name',
            'tags',
            'id'
        ]


class IngerdientSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='ingredient_name')

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit'
        )
