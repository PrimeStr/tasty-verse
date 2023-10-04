from re import search

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError('Нельзя использовать имя пользователя me')

    if not search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value):
        raise ValidationError(
            'В имени пользователя используются недопустимые символы')
