from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Follower(models.Model):
    subscriber = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribed = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
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