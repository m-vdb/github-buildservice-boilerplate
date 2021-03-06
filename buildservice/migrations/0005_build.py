# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-13 01:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildservice', '0004_webhook_github_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository', models.CharField(max_length=255)),
                ('sha', models.CharField(max_length=40)),
                ('pull_request_id', models.IntegerField(default=0)),
                ('pull_request_number', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
