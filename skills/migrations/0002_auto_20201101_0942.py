# Generated by Django 3.1.2 on 2020-11-01 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personassessment',
            name='levels',
        ),
        migrations.AddField(
            model_name='measurement',
            name='assessment',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='skills.personassessment'),
            preserve_default=False,
        ),
    ]
