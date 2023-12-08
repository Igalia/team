# Generated by Django 3.1.2 on 2022-12-01 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20221127_1711'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='device',
            name='manufacture_date',
        ),
        migrations.RemoveField(
            model_name='device',
            name='model_code',
        ),
        migrations.RemoveField(
            model_name='device',
            name='model_name',
        ),
        migrations.RemoveField(
            model_name='device',
            name='type',
        ),
        migrations.AddField(
            model_name='device',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='manufacture_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=50)),
                ('model_code', models.CharField(blank=True, max_length=50, null=True)),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.devicetype')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='model',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='inventory.devicemodel'),
            preserve_default=False,
        ),
    ]