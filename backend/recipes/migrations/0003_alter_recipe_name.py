# Generated by Django 3.2.19 on 2023-07-02 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=150, verbose_name='Название блюда'),
        ),
    ]