# Generated by Django 3.1.14 on 2023-12-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0013_auto_20221114_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='personaldata',
            name='avatar',
            field=models.ImageField(null=True, upload_to='people/personal_data/avatar'),
        ),
    ]
