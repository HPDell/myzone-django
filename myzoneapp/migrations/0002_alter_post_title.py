# Generated by Django 3.2.12 on 2022-03-16 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myzoneapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
