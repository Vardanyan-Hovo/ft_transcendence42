# Generated by Django 3.2.25 on 2024-05-18 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_person_is_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='history',
            name='oponent_points',
            field=models.IntegerField(default=0),
        ),
    ]
