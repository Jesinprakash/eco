# Generated by Django 5.0.6 on 2024-10-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystore', '0006_remove_ordersummary_cartitems_objects'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('honey', 'honey'), ('ghee', 'ghee')], default='honey', max_length=100),
        ),
    ]