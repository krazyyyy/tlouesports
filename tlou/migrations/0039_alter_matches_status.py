# Generated by Django 3.2.3 on 2021-06-06 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0038_auto_20210606_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matches',
            name='status',
            field=models.CharField(default='In-Progress', max_length=128),
        ),
    ]
