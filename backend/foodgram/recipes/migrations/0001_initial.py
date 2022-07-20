# Generated by Django 3.2.14 on 2022-07-20 07:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient_name', models.CharField(max_length=128, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(max_length=32, verbose_name='Единица измерения')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient_for_recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(max_length=10, verbose_name='Количество')),
                ('ingredient_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=32, verbose_name='Имя тега')),
                ('color', models.CharField(max_length=9)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe_name', models.CharField(db_index=True, help_text='Название рецепта', max_length=256, verbose_name='Название рецепта')),
                ('picture', models.ImageField(help_text='Изображение блюда', upload_to='', verbose_name='Изображение блюда')),
                ('text_description', models.TextField(help_text='Описание', max_length=1000, verbose_name='Описание')),
                ('cooking_time', models.TimeField(verbose_name='Время приготовления')),
                ('author', models.ForeignKey(help_text='Автор', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(related_name='recipies', through='recipes.Ingredient_for_recipe', to='recipes.Ingredient')),
                ('tag', models.ManyToManyField(related_name='recipies', to='recipes.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='ingredient_for_recipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]
