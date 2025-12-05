from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from .models import Follower


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 
        'is_staff', 'is_superuser',
        'is_active'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('date_joined', 'last_login')


class FollowerAdminForm(forms.ModelForm):
    """Форма для создания объекта модели Follower"""
    
    class Meta:
        model = Follower
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        subscriber = cleaned_data.get('subscriber')
        subscribed = cleaned_data.get('subscribed')

        if subscribed and subscriber:
            if subscriber == subscribed:
                self.add_error(
                    'subscribed',
                    'Нельзя подписаться на самого себя!'
                )

        return cleaned_data


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    form = FollowerAdminForm
    list_display = ('subscriber', 'subscribed')
    list_display_links = ('subscriber', 'subscribed')
    search_fields = (
        'subscriber__username',
        'subscriber__email',
        'subscribed__username',
        'subscribed__email'
    )
    autocomplete_fields = ('subscriber', 'subscribed')
