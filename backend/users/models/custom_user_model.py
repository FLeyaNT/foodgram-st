from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Такой email уже зарегистрирован.'
        }
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким юзернеймом уже существует.'
        },
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Юзернейм может содержать только буквы',
                    'цифры и символы: @.+-'
                ),
                code='invalid_username'
            )
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        upload_to='users/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
