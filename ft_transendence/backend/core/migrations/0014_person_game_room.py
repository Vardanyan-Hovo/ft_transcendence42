# Generated by Django 3.2.25 on 2024-03-20 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_person_ongoing'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='game_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants', to='core.gameroom'),
        ),
    ]
