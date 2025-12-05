from djoser.serializers import UserCreateSerializer

from rest_framework import serializers

from django.contrib.auth import get_user_model, password_validation

from utils.base64field import Base64ImageField


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастоиного пользователя"""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'avatar'
        )
        read_only_fields = ('id',)


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для для подписки на пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        from recipes.serializers import ShortRecipeSerializer
        return ShortRecipeSerializer(
            obj.recipes.all(),
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя"""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""

    current_password = serializers.CharField(
        required=True, write_only=True
    )
    new_password = serializers.CharField(
        required=True, write_only=True
    )

    def validate_current_password(self, value):
        request = self.context.get('request')
        user = request.user
        if isinstance(user, User):
            if not user.check_password(value):
                raise serializers.ValidationError({
                    'detail': 'Неверный текущий пароль'
                })
        return value

    def validate(self, attrs: dict):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        user = self.context['request'].user

        if current_password == new_password:
            raise serializers.ValidationError({
                'detail': 'Новый пароль совпадает со старым'
            })

        password_validation.validate_password(
            password=new_password,
            user=user
        )

        return attrs
