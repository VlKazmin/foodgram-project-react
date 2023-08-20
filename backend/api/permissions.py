from rest_framework.permissions import SAFE_METHODS, BasePermission


class Author(BasePermission):
    """Изменть и добовлять объекты может только автор."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class ReadOnly(BasePermission):
    """Только чтение."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """Только автор."""

    def has_object_permission(self, request, view, obj):
        if request.user.author:
            return True
