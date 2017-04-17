from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length=20)

class Person(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()

class UserInfo(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField()
    permission = models.CharField(max_length = 800)
    groups = models.CharField(max_length=800, null=True)

class GroupInfo(models.Model):
    name = models.CharField(max_length=40)
    permission = models.CharField(max_length = 800)
