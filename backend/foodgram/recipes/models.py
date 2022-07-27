from django.db import models
from users.models import User
from core.models import CreatedModel
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


class Recipe(CreatedModel):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=256,
        db_index=True,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/',
        help_text='Изображение блюда'
    )
    text = models.TextField(
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
    tags = models.ManyToManyField(
        Tag,
        related_name='recipies'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name


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
        return self.recipe.name


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        help_text='Подписчик',
        null=True
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Подписан на',
        help_text='Подписан на',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique follow'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite_for',
        verbose_name='Избранное для',
        help_text='Избранное для',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        verbose_name='Избранное',
        help_text='Избранное',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_list',
        verbose_name='Пользователь',
        help_text='Пользователь',
        on_delete=models.CASCADE
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_list',
        verbose_name='Список покупок',
        help_text='Список покупок'
    )

    def __str__(self):
        return f'{self.user.username} shopping list'
