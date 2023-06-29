import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, DateTimeField, F, ForeignKey, Model, Q
from django.db.models.functions import Length

models.CharField.register_lookup(Length)


def validate_user_name(value):
    reg = re.compile(r'^[\w.@+-]+\Z')
    if not reg.match(value):
        raise ValidationError(
            u'%s Не заполнено обязательное поле или оно заполнено некорректно'
        )
    if value.lower() == 'me':
        raise ValidationError(
            'Нельзя использовать это имя, выберите другое'
        )


class UserFoodgram(AbstractUser):
    """Пользователи."""
    username = models.CharField(
        verbose_name='Уникальное имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_user_name],
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )

    email = models.EmailField(unique=True)

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.username}'


class Subscriptions(Model):
    """Подписки и подписчики."""
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscribers',
        to=UserFoodgram,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Подписчики',
        related_name='subscriptions',
        to=UserFoodgram,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='\nRepeat subscription\n',
            ),
            models.CheckConstraint(
                check=~Q(author=F('user')),
                name='\nNo self sibscription\n'
            )
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
