# Generated by Django 5.0.4 on 2024-05-17 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listing', '0003_alter_preferredsubcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(choices=[('top', 'Top'), ('bottom', 'Bottom'), ('footwear', 'Footwear')], max_length=255, unique=True, verbose_name='Category Name'),
        ),
    ]