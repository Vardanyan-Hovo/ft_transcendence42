# Generated by Django 3.2.25 on 2024-05-21 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20240518_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='model',
            field=models.CharField(choices=[('easy', 'Easy'), ('classic', 'Classic'), ('hard', 'Hard')], default='easy', max_length=50),
        ),
    ]
