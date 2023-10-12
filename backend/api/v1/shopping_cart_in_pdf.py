from django.db.models import Sum
from django.http import HttpResponse
from weasyprint import HTML

from recipes.models import RecipeEssentials, Recipe


def generate_shopping_list_pdf(user):
    """
    Генерирует PDF-список покупок на основе рецептов, находящихся в
    корзине пользователя.

    Args:
        user (User): Пользователь, для которого генерируется список покупок.

    Returns:
        HttpResponse: HTTP-ответ с PDF-списком покупок в формате
        application/pdf.
    """
    recipes_in_cart = Recipe.objects.filter(shoppingcart__user=user)

    ingredients = RecipeEssentials.objects.filter(
        recipe__in=recipes_in_cart
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

    html_content = '<h1>Мой список покупок</h1><ul>'
    html_content += ''.join([
        f'<li>{ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]}) - '
        f'{ingredient["total_amount"]}</li>'
        for ingredient in ingredients.values('ingredient__name',
                                             'ingredient__measurement_unit',
                                             'total_amount')
    ])
    html_content += '</ul>'
    html_content += ('<div style="position: absolute; bottom: '
                     '100px; width: 100%; text-align: center; '
                     'font-size: 24px;">Foodgram</div>')

    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response[
        'Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'

    return response
