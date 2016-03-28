# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-28 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildservice', '0009_build_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='status',
            field=models.CharField(choices=[(b'success', b'Success'), (b'failure', b'Failure'), (b'errored', b'Errored'), (b'pending', b'Pending')], default=b'pending', max_length=10),
        ),
    ]