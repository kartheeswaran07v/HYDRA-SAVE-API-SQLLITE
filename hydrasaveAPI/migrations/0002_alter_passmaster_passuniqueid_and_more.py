# Generated by Django 4.2.5 on 2023-10-02 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hydrasaveAPI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passmaster',
            name='passUniqueId',
            field=models.CharField(default='PASS-<function uuid1 at 0x00000267F3EFCD60>', max_length=45),
        ),
        migrations.AlterField(
            model_name='trainmaster',
            name='trainUniqueId',
            field=models.CharField(default='TRAIN-<function uuid1 at 0x00000267F3EFCD60>', max_length=45),
        ),
    ]
