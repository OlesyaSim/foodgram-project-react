from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    Q,
    SET_NULL,
    SlugField,
    TextField,
    UniqueConstraint,
)
from colorful.fields import RGBColorField

User = get_user_model()

GREEN_COLOR = "#00ff00"
RED_COLOR = "#ff0000"
YELLOW_COLOR = "#ffff00"
BLACK_COLOR = "#000000"


class Tag(Model):
    """Тэги для рецептов."""
    name = CharField(
        verbose_name='Тэг',
        max_length=150,
        unique=True,
        blank=False,
    )
    color = RGBColorField(colors=[GREEN_COLOR, RED_COLOR, YELLOW_COLOR],
                          max_length=10,
                          verbose_name="цвет тэга",
                          unique=True,
                          blank=False,
                          )
    slug = SlugField(
        verbose_name='Слаг тэга латинскими буквами',
        max_length=150,
        unique=True,
        db_index=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = (UniqueConstraint(
                fields=('name', 'color'),
                name='unique_for_tag'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Product(Model):
    """Модель продукта."""
    name = CharField(
        verbose_name='Продукт',
        max_length=150,
    )
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient'
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(Model):
    """Модель описывает рецепты."""
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=SET_NULL,
        blank=False,
        null=True,
    )
    name = CharField(
        verbose_name='Название блюда',
        max_length=150,
        blank=False
    )
    image = ImageField(
        verbose_name='Фото блюда',
        upload_to='recipe_images/',
        blank=True,
        null=True
    )
    text = TextField(
        verbose_name='Описание блюда',
        max_length=5000,
        blank=False
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        to=Product,
        through='Ingredients',
        blank=False
    )
    tags = ManyToManyField(
        verbose_name='Тег',
        related_name='recipes',
        to='Tag',
        blank=False
    )
    cooking_time = PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                1,
                'Время приготовления должно быть больше 0.',
            ),
        ),
        blank=False
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author}'


class Ingredients(Model):
    """Количество продуктов в конкретном блюде.
    Модель связывает Recipe и Product с указанием количества продукта для
    вывода его в список покупок.
    """

    recipe = ForeignKey(
        verbose_name='В каких рецептах',
        related_name='product',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        verbose_name='Ингредиенты из рецепта',
        related_name='recipe',
        to=Product,
        on_delete=CASCADE,
    )
    amount = PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(1,
                              'Количество ингредиента должно быть больше 0.',
                              ),
        )
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('recipe',)
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients',),
                name='\n%(app_label)s_%(class)s ingredient already added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class FavoritesRecipes(Model):
    """Избранные рецепты. Модель связывает Recipe и User."""
    recipe = ForeignKey(
        verbose_name='Избранные рецепты',
        related_name='in_favorites',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='favorites',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is favorite already\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Cart(Model):
    """Рецепты в списке покупок. Модель связывает Recipe и User."""
    recipe = ForeignKey(
        verbose_name='Список покупок (Корзина)',
        related_name='in_cart',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Владелец списка',
        related_name='cart',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is cart already\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
