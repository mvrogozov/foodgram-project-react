from django.db import transaction
from rest_framework import serializers

from recipes.models import (Favorite, Follow, Ingredient, IngredientForRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import User
from .fields import Base64ImageField
from .utils import is_me


class PasswordSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        return {
            'current_password': data['current_password'],
            'new_password': data['new_password']
        }

    def validate(self, data):
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
        return data


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


class UserPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    @transaction.atomic()
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        return is_me(value)


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='tag_name')

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_name')

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class ForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient_name.id')
    name = serializers.ReadOnlyField(source='ingredient_name.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient_name.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ForRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient_name'
    )

    class Meta:
        model = IngredientForRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = ForRecipeSerializer(
        source='ingredient',
        many=True
    )
    author = UserSerializer()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        if self.context:
            user = self.context.get('request').user
            return Favorite.objects.filter(user=user.id, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context:
            user = self.context.get('request').user
            return ShoppingCart.objects.filter(
                user=user.id, recipe=obj
                ).exists()
        return False


class RecipePostSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = ForRecipePostSerializer(
        many=True,
        source='ingredient'
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'text',
            'ingredients',
            'cooking_time',
            'image',
            'tags'
        )

    def validate_ingredients(self, value):
        collection = []
        for item in value:
            if item['ingredient_name'] in collection:
                raise serializers.ValidationError(
                    'Переданы дублированные ингредиенты'
                )
            collection.append(item['ingredient_name'])
        return value

    def validate_tags(self, value):
        collection = []
        for item in value:
            if item in collection:
                raise serializers.ValidationError(
                    'Переданы дублированные тэги'
                )
            collection.append(item)
        return value

    def validate(self, attrs):
        user = self.context.get('request').user
        if self.context.get('request').method == 'PATCH':
            pk = self.context['view'].kwargs.get('pk')
            if Recipe.objects.get(pk=pk).name == attrs['name']:
                return attrs
        if Recipe.objects.filter(name=attrs['name'], author=user):
            raise serializers.ValidationError(
                'У Вас есть рецепт с таким именем'
            )
        return attrs

    def _collect_ingredients(self, ingredients, recipe):
        ingredients_to_add = []
        for ingredient in ingredients:
            ingredient_instance = ingredient.get('ingredient_name')
            ingredients_to_add.append(IngredientForRecipe(
                ingredient_name=ingredient_instance,
                recipe=recipe,
                amount=ingredient.get('amount')
            ))
        IngredientForRecipe.objects.bulk_create(ingredients_to_add)
        return ingredients_to_add

    @transaction.atomic()
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=author)
        self._collect_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic()
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        IngredientForRecipe.objects.filter(recipe=instance).delete()
        self._collect_ingredients(ingredients, instance)
        instance.tags.set(tags)
        return instance


class ShortRecipeSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserFollowSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes_count = serializers.IntegerField()
    author = UserFollowSerializer()

    class Meta:
        model = Follow
        fields = (
            'author',
            'recipes_count'
        )
