# Generated by Django 5.0.6 on 2024-10-15 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mystore', '0011_alter_ordersummary_payment_methode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='pro_cat_object',
        ),
        migrations.DeleteModel(
            name='Product_Category',
        ),
    ]