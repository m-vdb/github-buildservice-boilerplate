# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-27 21:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildservice', '0007_auto_20160327_2134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
