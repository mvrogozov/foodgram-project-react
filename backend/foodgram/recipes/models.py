from django.db import models
from users.models import User
from djangoHexadecimal.fields import HexadecimalField


class Ingredient(models.Model):
    ingredient_name = models.CharField(
        'Название ингредиента',
        max_length=128
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=32
    )

    def __str__(self):
        return self.ingredient_name


class Tag(models.Model):
    tag_name = models.CharField(
        'Имя тега',
        max_length=32
    )
    color = models.CharField(
        max_length=9
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.tag_name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор'
    )
    recipe_name = models.CharField(
        'Название рецепта',
        max_length=256,
        db_index=True,
        help_text='Название рецепта'
    )
    picture = models.ImageField(
        'Изображение блюда',
        help_text='Изображение блюда'
    )
    text_description = models.TextField(
        'Описание',
        max_length=1000,
        help_text='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Ingredient_for_recipe',
        related_name='recipies',
        verbose_name='Список ингредиентов'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipies'
    )
    cooking_time = models.TimeField(
        'Время приготовления',
        auto_now_add=False
    )

    def __str__(self):
        return self.recipe_name


class Ingredient_for_recipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient_name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        'Количество',
        max_length=10
    )

    def __str__(self):
        return self.recipe.recipe_name
