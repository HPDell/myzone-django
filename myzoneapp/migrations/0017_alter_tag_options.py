# Generated by Django 3.2.12 on 2022-03-22 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myzoneapp', '0016_auto_20220322_1121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'default_manager_name': 'objects'},
        ),
    ]
