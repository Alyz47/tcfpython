# Generated by Django 5.0.4 on 2024-05-17 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_order_order_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='created',
        ),
        migrations.RemoveField(
            model_name='order',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='order',
            name='uuid',
        ),
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=50),
        ),
    ]
