# Generated by Django 3.2.3 on 2021-06-05 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0030_alter_userdtl_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='crown_held',
            field=models.IntegerField(default=0),
        ),
    ]
