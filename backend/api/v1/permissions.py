from rest_framework import permissions


class IsAuthenticated:
    pass


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False  # Если пользователь не аутентифицирован, нет доступа
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)

