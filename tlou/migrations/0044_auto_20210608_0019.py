# Generated by Django 3.2.3 on 2021-06-07 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0043_auto_20210607_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='matches',
            name='team_one_rating',
            field=models.CharField(default='', max_length=64),
        ),
        migrations.AddField(
            model_name='matches',
            name='team_two_rating',
            field=models.CharField(default='', max_length=64),
        ),
    ]
