# Generated by Django 3.1.6 on 2021-04-02 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webinarsession',
            name='nickname',
        ),
        migrations.RemoveField(
            model_name='webinarsession',
            name='organization_id',
        ),
        migrations.RemoveField(
            model_name='webinarsession',
            name='user_id',
        ),
    ]
