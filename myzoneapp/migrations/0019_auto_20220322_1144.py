# Generated by Django 3.2.12 on 2022-03-22 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myzoneapp', '0018_auto_20220322_1141'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='name_zh_CN',
            new_name='name_zh_cn',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='name_zh_CN',
            new_name='name_zh_cn',
        ),
    ]
