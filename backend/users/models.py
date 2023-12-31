from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants.users import (EMAIL_LENGTH, NAME_LENGTH,
                                  ROLE_LENGTH, USERNAME_LENGTH)
from users.validators import validate_username


class User(AbstractUser):
    """
    Модель пользователя приложения.

    Поля:
        - username (str): Юзернейм пользователя (уникальное).
        - email (str): Адрес электронной почты (уникальный).
        - first_name (str): Имя пользователя.
        - last_name (str): Фамилия пользователя.
        - role (str): Роль пользователя (из выбора в ROLES).

    Мета:
        - ordering (list): Сортировка объектов модели по умолчанию.
        - verbose_name (str): Название модели в единственном числе.
        - verbose_name_plural (str): Название модели во множественном числе.

    Методы:
        - is_admin: Проверяет, является ли пользователь администратором.

    Пример:
        user = User.objects.get(username='example')
        print(user.is_admin) Выведет True, если пользователь - администратор.
    """
    USER = 'user'
    ADMIN = 'admin'

    ROLES = (
        (USER, USER),
        (ADMIN, ADMIN)
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    username = models.CharField(
        'Имя пользователя',
        validators=(validate_username,),
        max_length=USERNAME_LENGTH,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_LENGTH,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_LENGTH,
        blank=False,
        null=False
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_LENGTH,
        choices=ROLES,
        default=USER,
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Модель подписки между пользователями приложения.

    Поля:
        - subscriber (User): Подписчик (пользователь, который подписывается).
        - target_user (User): Целевой пользователь (на которого подписываются).
        - created_at (datetime): Дата создания подписки.

    Мета:
        - unique_together (tuple): Уникальные пары подписчиков и
        целевых пользователей.
        - verbose_name (str): Название модели в единственном числе.
        - verbose_name_plural (str): Название модели во множественном числе.

    Пример:
        subscription = Subscription.objects.get(pk=1)
        print(subscription) Выведет строку в
        формате "Подписчик -> Целевой пользователь".
    """
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='target_user',
        verbose_name='Целевой пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        unique_together = ('subscriber', 'target_user')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} -> {self.target_user}'
