# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 05:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildservice', '0011_repository_default_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='number',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='repository',
            name='build_count',
            field=models.IntegerField(default=0),
        ),
    ]
