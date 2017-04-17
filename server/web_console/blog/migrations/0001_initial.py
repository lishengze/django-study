# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-28 06:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(verbose_name='\u5b58\u6863\u65e5\u671f')),
            ],
            options={
                'verbose_name': '\u5b58\u6863\u4fe1\u606f',
                'verbose_name_plural': '\u5b58\u6863\u4fe1\u606f\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(max_length=25, verbose_name='\u56de\u590d\u8005\u540d\u79f0')),
                ('email', models.EmailField(max_length=25, verbose_name='\u56de\u590d\u8005Email')),
                ('content', models.TextField(max_length=200, verbose_name='\u56de\u590d\u5185\u5bb9')),
                ('pub_date', models.DateTimeField(verbose_name='\u56de\u590d\u65e5\u671f')),
            ],
            options={
                'verbose_name': '\u56de\u590d',
                'verbose_name_plural': '\u56de\u590d\u4fe1\u606f\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Essay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=25, verbose_name='\u6587\u7ae0\u6807\u9898')),
                ('content', models.TextField(max_length=2000, verbose_name='\u6587\u7ae0\u5185\u5bb9')),
                ('abstract', models.TextField(max_length=150, verbose_name='\u6587\u7ae0\u6458\u8981')),
                ('pub_date', models.DateTimeField(verbose_name='\u53d1\u8868\u65e5\u671f')),
                ('view_count', models.IntegerField(default=0, verbose_name='\u6d4f\u89c8\u6b21\u6570')),
            ],
            options={
                'ordering': ['-pub_date'],
                'verbose_name': '\u6587\u7ae0',
                'verbose_name_plural': '\u6587\u7ae0\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='EssayType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('tname', models.CharField(max_length=25, verbose_name='\u6587\u7ae0\u7c7b\u540d')),
                ('baseType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.EssayType', verbose_name='\u6240\u5c5e\u7c7b\u522b')),
            ],
            options={
                'ordering': ['tname'],
                'verbose_name': '\u6587\u7ae0\u7c7b\u578b',
                'verbose_name_plural': '\u6587\u7ae0\u7c7b\u578b\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='LevelMsg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(max_length=25, verbose_name='\u7559\u8a00\u8005\u540d\u79f0')),
                ('content', models.TextField(max_length=200, verbose_name='\u7559\u8a00\u5185\u5bb9')),
                ('email', models.EmailField(max_length=25, verbose_name='\u7559\u8a00\u8005Email')),
            ],
            options={
                'verbose_name': '\u7559\u8a00\u677f',
                'verbose_name_plural': '\u7559\u8a00\u4fe1\u606f\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uname', models.CharField(max_length=25, verbose_name='\u7528\u6237\u540d')),
                ('pwd', models.CharField(max_length=12, verbose_name='\u5bc6\u7801')),
                ('sex', models.CharField(choices=[('M', '\u7537'), ('F', '\u5973')], max_length=1, verbose_name='\u6027\u522b')),
                ('email', models.CharField(max_length=25)),
                ('last_login_ip', models.GenericIPAddressField(verbose_name='\u6700\u540e\u767b\u5f55IP')),
                ('last_login_date', models.DateTimeField(verbose_name='\u6700\u540e\u767b\u5f55\u65e5\u671f')),
            ],
            options={
                'verbose_name': '\u7528\u6237',
                'verbose_name_plural': '\u7528\u6237\u5217\u8868',
            },
        ),
        migrations.AddField(
            model_name='essay',
            name='eType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.EssayType', verbose_name='\u6240\u5c5e\u7c7b\u522b'),
        ),
        migrations.AddField(
            model_name='comment',
            name='essay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essay_comment', to='blog.Essay'),
        ),
        migrations.AddField(
            model_name='archive',
            name='essay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archive_essay', to='blog.Essay'),
        ),
    ]
