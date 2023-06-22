import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0005_auto_20230615_1258'),
    ]
    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='amount',
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator
                            (1, 'Количество ингредиента не может быть '
                                'меньше 1.')],
                verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator
                            (1, 'Время приготовления должно быть больше 0.')],
                verbose_name='Время приготовления'),
        ),
    ]
