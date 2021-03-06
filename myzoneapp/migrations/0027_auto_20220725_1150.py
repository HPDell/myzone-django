# Generated by Django 3.2.12 on 2022-07-25 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myzoneapp', '0026_auto_20220502_1826'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostPermanent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='permanent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myzoneapp.postpermanent'),
        ),
        migrations.CreateModel(
            name='PostTranslate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('zh-cn', 'Chinese')], max_length=7)),
                ('permanent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myzoneapp.postpermanent')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myzoneapp.post')),
            ],
            options={
                'unique_together': {('permanent', 'language')},
            },
        ),
    ]
