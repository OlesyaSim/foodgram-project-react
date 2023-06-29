from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Product, Tag


class Command(BaseCommand):
    help = 'Загружает данные из csv файла в базу данных'

    def handle(self, *args, **kwargs):
        for row in DictReader(open(
                'data/ingredients.csv',
                encoding="utf8")):
            Product.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit'],
            )

        for row in DictReader(open(
                'data/tags.csv',
                encoding="utf8")):
            Tag.objects.get_or_create(
                name=row['name'],
                color=row['color'],
                slug=row['slug'],
            )
        self.stdout.write(
            'Данные ингредиентов и тэгов загружены в базу данных'
        )
