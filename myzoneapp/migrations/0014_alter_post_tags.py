# Generated by Django 3.2.12 on 2022-03-19 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myzoneapp', '0013_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='myzoneapp.Tag'),
        ),
    ]
