# Generated by Django 3.2.3 on 2021-06-15 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0068_auto_20210615_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banip',
            name='ban_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='image',
            field=models.ImageField(blank=True, default='media/profile/LOGO_BLACK_PNG.png', null=True, upload_to='media/Teams'),
        ),
        migrations.AlterField(
            model_name='userdtl',
            name='img_user',
            field=models.ImageField(blank=True, default='media/profile/LOGO_BLACK_PNG.png', null=True, upload_to='media/profile'),
        ),
    ]
