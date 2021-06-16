# Generated by Django 3.2.3 on 2021-06-13 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0054_auto_20210613_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminoptions',
            name='home_notice',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adminoptions',
            name='home_video',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='ladders',
            name='lock_ladder',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='adminoptions',
            name='about_image',
            field=models.ImageField(blank=True, null=True, upload_to='media/support'),
        ),
    ]
