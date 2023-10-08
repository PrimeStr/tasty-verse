from rest_framework.pagination import PageNumberPagination

from core.constants.settings import PAGINATION_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация.
    page - номер страницы(integer).
    limit- количество объектов на странице(integer)."""
    page_size_query_param = 'limit'
    page_size = PAGINATION_PAGE_SIZE
