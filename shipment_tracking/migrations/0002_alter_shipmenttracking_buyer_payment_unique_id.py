# Generated by Django 4.1.7 on 2023-04-14 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipment_tracking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipmenttracking',
            name='buyer_payment_unique_id',
            field=models.CharField(default='xxx', max_length=50, verbose_name='Buyer Unique ID'),
        ),
    ]
