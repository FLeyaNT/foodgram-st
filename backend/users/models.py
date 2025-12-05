from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.hashers import make_password


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
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def save(self, *args, **kwargs):
        if (
            self.password and len(self.password) < 50
            and not self.password.startswith('pbkdf2_')
        ):
            self.password = make_password(self.password)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username


class Follower(models.Model):
    """Модель подписки"""

    subscriber = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    subscribed = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'subscribed'),
                name='unique_follow`'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscribed')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'Подписка {self.subscriber} на {self.subscribed}'
