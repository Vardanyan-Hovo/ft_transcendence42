# Generated by Django 3.2.25 on 2024-03-08 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_person_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='background',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='gamemode',
            field=models.CharField(default='classic', max_length=100),
        ),
        migrations.AddField(
            model_name='person',
            name='live',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='loses',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='person',
            name='wins',
            field=models.IntegerField(default=0),
        ),
    ]
