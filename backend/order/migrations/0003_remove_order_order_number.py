# Generated by Django 5.0.4 on 2024-05-17 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_created_at_order_listing_order_seller_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_number',
        ),
    ]
