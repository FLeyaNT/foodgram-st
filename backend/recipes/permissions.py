from rest_framework import permissions
from rest_framework.request import Request

from .models import Recipe


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Класс ограничения для владельцев рецепта"""

    def has_object_permission(self, request: Request, view, obj: Recipe):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author
