# Generated by Django 4.2.5 on 2023-10-07 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hydrasaveAPI', '0003_alter_passmaster_passuniqueid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermaster',
            name='cookies',
            field=models.CharField(default='ABCDEFGH', max_length=100),
        ),
    ]
