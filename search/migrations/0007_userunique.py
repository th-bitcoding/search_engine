# Generated by Django 4.2.4 on 2023-10-11 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_searchafg'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserUnique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=10, unique=True)),
                ('flag', models.BooleanField()),
            ],
        ),
    ]
