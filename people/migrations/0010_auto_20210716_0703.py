# Generated by Django 3.1.2 on 2021-07-16 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0009_team_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
