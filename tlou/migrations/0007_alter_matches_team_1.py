# Generated by Django 3.2.3 on 2021-05-31 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tlou', '0006_matches_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matches',
            name='team_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team_A', to='tlou.team'),
        ),
    ]
