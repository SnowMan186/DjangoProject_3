from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        is_owner = obj.owner == request.user
        is_admin = request.user.is_staff

        is_moderator_patch = (request.method == 'PATCH' and request.user.groups.filter(name='moderators').exists())

        return is_owner or is_admin or is_moderator_patch


class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы "модераторы".
    Проверка на уровне View (has_permission).
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()