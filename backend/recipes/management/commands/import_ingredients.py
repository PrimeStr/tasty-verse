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
        - Убедитесь, что путь к файлу 'core/ingredients.csv' настроен в
        соответствии с расположением файла import_ingredients.py (файлы должны
        лежать в одной директории)
    """
    help = 'Import data from a CSV file into the Ingredient model'

    def handle(self, *args: Any, **options: Any) -> str:
        try:
            self.import_ingredients()
            self.stdout.write(self.style.SUCCESS('Ингредиенты успешно '
                                                 'импортированы в БД.'))
        except Exception as error:
            self.stderr.write('Ошибка при импорте ингредиентов:', str(error))
        return self.stderr.write('Операция импорта завершена.')

    def import_ingredients(self, file: str = 'core/ingredients.csv') -> None:
        with open(file, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
