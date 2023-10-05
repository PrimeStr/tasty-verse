from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from backend.settings import (COLORFIELD_LENGTH, INGREDIENT_LENGTH, RECIPE_NAME_LENGTH,
                              TAG_LENGTH, MIN_COOKING_TIME, MAX_COOKING_TIME)
from users.models import User


class Ingredient(models.Model):
    """
    Модель ингредиента для рецепта. Один ингредиент может быть у многих рецептов.

    Поля:
    - name (CharField): Название ингредиента для рецепта.
    - measurement_unit (CharField): Единица измерения для ингредиента.

    Мета:
    - verbose_name (str): Название модели в единственном числе.
    - verbose_name_plural (str): Название модели во множественном числе.
    - ordering (list): Сортировка объектов модели по умолчанию.

    Методы:
    - __str__(): Возвращает строковое представление ингредиента в формате "Название, Единица измерения".

    """
    name = models.CharField(
        verbose_name='Название ингредиента для рецепта',
        max_length=INGREDIENT_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=INGREDIENT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тег рецепта.
    M2M с Recipe."""
    name = models.CharField(
        verbose_name='Название тега для рецепта',
        max_length=TAG_LENGTH,
        unique=True,
        # required=True
    )
    color = ColorField(
        verbose_name='Цвет в формате HEX',
        format='hex',
        max_length=COLORFIELD_LENGTH,
        default='#FF0000',
    )
    slug = models.SlugField(
        verbose_name='Slug названия тега',
        max_length=TAG_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=(f'Slug должен содержать только буквы (строчные и '
                         f'заглавные), цифры, дефисы и подчеркивания.'),
                code='invalid_slug'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты блюда',
        through='recipes.RecipeEssentials'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME_LENGTH,
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        upload_to='recipe_images/'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME,
                              message=f'Время приготовления должно '
                                      f'быть не менее {MIN_COOKING_TIME} мин.'),
            MaxValueValidator(MAX_COOKING_TIME,
                              message=f'Время приготовления должно '
                                      f'быть не более {MAX_COOKING_TIME} мин.'),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeEssentials(models.Model):
    """Ингредиенты в рецепте.
    Определение количества ингредиентов в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        # related_name='list_of_ingredient',
        verbose_name='Ингредиенты в рецепте'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
    )

    class Meta:
        # default_related_name = 'ingredients_in_recipe'
        verbose_name = 'Состав рецепта'
        verbose_name_plural = 'Состав рецептов'

    def __str__(self):
        return f'{self.ingredient} – {self.amount}'


class Favorite(models.Model):
    """Избранные рецепты у пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
        verbose_name='Рецепт',
    )
    add_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уже в избранном!',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Корзина пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уже в корзине!',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
