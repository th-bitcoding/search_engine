# Generated by Django 4.2.4 on 2023-09-06 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_channel_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='search_data',
            field=models.CharField(max_length=100),
        ),
    ]
