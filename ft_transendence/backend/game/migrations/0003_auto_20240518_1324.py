# Generated by Django 3.2.25 on 2024-05-18 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_round'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameinvite',
            name='accepted',
            field=models.BooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='gameinvite',
            name='rejected',
            field=models.BooleanField(default=None),
        ),
    ]