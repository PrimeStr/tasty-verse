from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
        Пользовательские разрешения для проверки администратора или только для чтения.

        Разрешает доступ только для чтения (GET, HEAD, OPTIONS) пользователям, если
        они не являются администраторами. Для администраторов разрешены все методы.

        Attributes:
            - has_permission (method): Проверяет разрешение на уровне представления.

    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
        Пользовательские разрешения для проверки авторства, администратора или только для чтения.

        Разрешает доступ только для чтения (GET, HEAD, OPTIONS) пользователям,
        а также разрешает редактирование объекта только его авторам или администраторам.

        Attributes:
            - has_permission (method): Проверяет разрешение на уровне представления.
            - has_object_permission (method): Проверяет разрешение на уровне объекта.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_admin
