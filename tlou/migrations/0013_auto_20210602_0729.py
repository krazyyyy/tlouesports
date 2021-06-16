# Generated by Django 3.2.3 on 2021-06-02 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0012_auto_20210601_1905'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matches',
            old_name='result',
            new_name='result_team_1',
        ),
        migrations.AddField(
            model_name='matches',
            name='result_team_2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='matches',
            name='winner',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='about',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
