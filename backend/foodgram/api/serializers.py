import base64
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Tag, Ingredient_for_recipe, Follow
from django.core.files.base import ContentFile
from users.models import User
from .utils import is_me


class PasswordSerializer(serializers.BaseSerializer):
    
    def to_representation(self, instance):
        return super().to_representation(instance)

    def to_internal_value(self, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not current_password:
            raise serializers.ValidationError({
                'current_password': 'Обязательное поле'
            })
        if not new_password:
            raise serializers.ValidationError({
                'new_password': 'Обязательное поле'
            })
        if len(new_password) < 8:
            raise serializers.ValidationError(
                'Длина пароля должна быть не меньше 8 символов'
            )
        return {
            'current_password': current_password,
            'new_password': new_password
        }


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context:
            user = self.context.get('request').user
            return Follow.objects.filter(user=user.id, author=obj).exists()
        return False

    def validate_username(self, value):
        return is_me(value)


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


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit'
        )


class Ingredient_for_recipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_name')

    class Meta:
        model = Ingredient_for_recipe
        fields = ('id', 'amount')


class ForRecipeSerializer(serializers.Field):

    def to_representation(self, value):
        ingredient_data = value.all()
        out_data = []
        for item in ingredient_data:
            out_data.append({
                'id': item.id,
                'name': item.ingredient_name.name,
                'measurement_unit': item.ingredient_name.measurement_unit,
                'amount': item.amount
            })
        return out_data

    def to_internal_value(self, data):
        serializer = Ingredient_for_recipeSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = ForRecipeSerializer(
        source='ingredient'
    )

    class Meta:
        model = Recipe
        fields = [
            'name',
            'author',
            'text',
            'id',
            'ingredients',
            'cooking_time',
            'image',
            'tags',
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'name'),
                message=('У Вас есть рецепт с таким именем')
            )
        ]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_instance = get_object_or_404(
                Ingredient,
                pk=ingredient.get('ingredient_name')
            )
            Ingredient_for_recipe.objects.get_or_create(
                ingredient_name=ingredient_instance,
                recipe=recipe,
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.filter(pk=instance.id)
        recipe.update(**validated_data)
        Ingredient_for_recipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            ingredient_instance = get_object_or_404(
                Ingredient,
                pk=ingredient.get('ingredient_name')
            )
            Ingredient_for_recipe.objects.get_or_create(
                ingredient_name=ingredient_instance,
                recipe=instance,
                amount=ingredient.get('amount')
            )
        instance.tags.set(tags)
        return instance
