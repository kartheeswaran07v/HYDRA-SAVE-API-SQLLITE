# Generated by Django 4.2.5 on 2023-10-08 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hydrasaveAPI', '0004_usermaster_cookies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermaster',
            name='isActive',
            field=models.BooleanField(default=True, help_text='1-True, 0-False'),
        ),
    ]