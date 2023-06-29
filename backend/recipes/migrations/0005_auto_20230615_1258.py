# Generated by Django 3.2.19 on 2023-06-15 12:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_image'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipe',
            name='unique_for_author',
        ),
        migrations.RemoveConstraint(
            model_name='recipe',
            name='\nrecipes_recipe_name is empty\n',
        ),
        migrations.AlterField(
            model_name='cart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart', to='recipes.recipe', verbose_name='Список покупок (Корзина)'),
        ),
        migrations.AlterField(
            model_name='favoritesrecipes',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_favorites', to='recipes.recipe', verbose_name='Избранные рецепты'),
        ),
    ]
