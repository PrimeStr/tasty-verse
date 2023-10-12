# Generated by Django 3.2.3 on 2023-10-12 18:10

import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0008_rename_ingredientinrecipe_recipeessentials'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name'], 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='Уже в избранном!',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='Уже в корзине!',
        ),
        migrations.AlterField(
            model_name='favorite',
            name='add_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления в избранное'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Единица измерения ингредиента'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=200, verbose_name='Название ингредиента для рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='recipeessentials',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Количество ингредиента должно быть не менее 1 ед.'), django.core.validators.MaxValueValidator(1000, message='Количество ингредиента должно быть не менее 1000 ед.')], verbose_name='Количество ингредиентов'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=7, samples=None, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_color', message='Color должен начинаться со знака # и содержать только цифры и заглавные английские буквы.', regex='^#([A-F0-9]{6})$')], verbose_name='Цвет в формате HEX'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_slug', message='Slug должен содержать только буквы (строчные и заглавные), цифры, дефисы и подчеркивания.', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Slug тега'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='Рецепт уже в избранном!'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='Такой ингредиент уже есть!'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='Рецепт уже в корзине!'),
        ),
    ]