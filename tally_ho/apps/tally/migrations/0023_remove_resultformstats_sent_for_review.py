# Generated by Django 2.1.1 on 2020-03-12 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tally', '0022_auto_20200312_0715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resultformstats',
            name='sent_for_review',
        ),
    ]
