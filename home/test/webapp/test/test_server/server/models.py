from __future__ import unicode_literals

from django.db import models

# Create your models here.
class UserInfo(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField()
    permission = models.CharField(max_length = 800, null=True)
    groups = models.CharField(max_length=800, null=True)
    password = models.CharField(max_length=20, null=True)

class GroupInfo(models.Model):
    name = models.CharField(max_length=40)
    permission = models.CharField(max_length = 800, null=True)
