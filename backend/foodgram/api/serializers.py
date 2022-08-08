import base64
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Tag, Ingredient_for_recipe
from recipes.models import Follow, Favorite, ShoppingCart
from django.core.files.base import ContentFile
from users.models import User
from .utils import is_me
from django.db import transaction


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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
    image = Base64ImageField(use_url=True)
    ingredients = ForRecipeSerializer(
        source='ingredient'
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

    def validate(self, attrs):
        user = self.context.get('request').user
        if Recipe.objects.filter(name=attrs['name'], author=user):
            raise serializers.ValidationError(
                'У Вас есть рецепт с таким именем'
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=author)
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

    @transaction.atomic()
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.filter(pk=instance.id)
        recipe.update(**validated_data)
        instance.image = image
        instance.save()
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
        instance.refresh_from_db()
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

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes'
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
