# Generated by Django 3.2.3 on 2021-06-08 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0044_auto_20210608_0019'),
    ]

    operations = [
        migrations.AddField(
            model_name='matches',
            name='disputed',
            field=models.BooleanField(default=False),
        ),
    ]
