# Generated by Django 5.0.6 on 2024-09-29 07:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystore', '0004_rename_user_onject_reviews_user_object'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='product_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='mystore.productvarient'),
        ),
    ]
