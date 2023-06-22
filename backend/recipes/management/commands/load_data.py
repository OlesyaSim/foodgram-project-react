from csv import DictReader
from django.core.management import BaseCommand

from recipes.models import Product


class Command(BaseCommand):
    help = 'Загружает данные из csv файла в базу данных'

    def handle(self, *args, **kwargs):
        for row in DictReader(open(
                'data/ingredients.csv',
                encoding="utf8")):
            product = Product(
                name=row['name'],
                measurement_unit=row['measurement_unit'],
            )
            product.save()
            self.stdout.write('Данные загружены в базу данных')
