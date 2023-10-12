# Generated by Django 4.2.4 on 2023-08-25 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_data', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='SubObjectJSON',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_objects', models.JSONField()),
            ],
        ),
    ]
