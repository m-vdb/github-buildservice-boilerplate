# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-11 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildservice', '0003_oauthtoken_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhook',
            name='github_id',
            field=models.IntegerField(default=0),
        ),
    ]