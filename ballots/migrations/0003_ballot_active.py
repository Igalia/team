# Generated by Django 3.1.2 on 2020-12-21 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0002_auto_20201214_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]