# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-24 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_group3'),
    ]

    operations = [
        migrations.AddField(
            model_name='group2',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
