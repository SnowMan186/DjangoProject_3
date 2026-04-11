from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_staff

from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы "модераторы".
    Проверка на уровне View (has_permission).
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()