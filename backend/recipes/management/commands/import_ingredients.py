import csv
from typing import Any

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда управления Django для импорта данных из CSV-файла в
    модель Ingredient.

    Эта команда читает данные из CSV-файла и импортирует их в модель Ingredient
    в базе данных.

    Пример использования:
        python manage.py import_ingredients

    Эта команда будет обновлять существующие ингредиенты или создавать новые на
    основе данных в CSV-файле.

    Вывод:
        - Успешный импорт: Выводит сообщение об успешном выполнении.
        - Ошибка импорта: Выводит сообщение об ошибке.

    Примечание:
        - Убедитесь, что файл 'ingredients.csv' лежит в правильной
        директории 'core/ingredients.csv'.
    """
    help = 'Import data from a CSV file into the Ingredient model'

    def handle(self, *args: Any, **options: Any) -> str:
        """
        Обработка команды для импорта ингредиентов.

        Args:
            *args (Any): Позиционные аргументы.
            **options (Any): Ключевые аргументы.

        Returns:
            str: Результат выполнения операции импорта.
        """
        try:
            self.import_ingredients()
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы в БД.'))
        except Exception as error:
            self.stderr.write('Ошибка при импорте ингредиентов:', str(error))
        return self.stdout.write(self.style.SUCCESS(
            'Операция импорта завершена.'))

    @staticmethod
    def import_ingredients(file: str = 'core/ingredients.csv') -> None:
        """
        Импорт ингредиентов из CSV-файла и сохранение их в базу данных.

        Args:
            file (str): Путь к CSV-файлу с ингредиентами.
            По умолчанию, 'core/ingredients.csv'.
        """
        ingredients_to_create = []
        with open(file, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                name, measurement_unit = row[0], row[1]
                ingredient = Ingredient(name=name,
                                        measurement_unit=measurement_unit)
                ingredients_to_create.append(ingredient)

        Ingredient.objects.bulk_create(ingredients_to_create,
                                       ignore_conflicts=True)
