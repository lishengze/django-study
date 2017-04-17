# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-25 04:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('permission', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('email', models.EmailField(max_length=254)),
                ('permission', models.CharField(max_length=400)),
            ],
        ),
    ]
