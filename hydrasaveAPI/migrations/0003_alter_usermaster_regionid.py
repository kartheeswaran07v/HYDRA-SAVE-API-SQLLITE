# Generated by Django 4.2.5 on 2023-09-25 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hydrasaveAPI', '0002_alter_plantmaster_createdbyid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermaster',
            name='regionID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hydrasaveAPI.regionmaster'),
        ),
    ]
