# Generated by Django 4.2.4 on 2023-09-12 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_favourite'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchAfg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_file', models.JSONField()),
            ],
        ),
    ]
