# Generated by Django 3.1.2 on 2022-11-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0010_auto_20210716_0703'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='full_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='join_date',
            field=models.DateField(null=True),
        ),
    ]
