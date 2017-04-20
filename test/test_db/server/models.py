from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Persion(models.Model):
	name = models.CharField(max_length = 20)
	age = models.IntegerField()

class Person(models.Model):
	name = models.CharField(max_length = 20)
	age = models.IntegerField()	

class Group(models.Model):
	name = models.CharField(max_length = 30)
	scale = models.IntegerField()

class Group2(models.Model):
	name = models.CharField(max_length = 30)
	scale = models.IntegerField()
	description = models.CharField(max_length = 200, null=True)

class Group3(models.Model):
	name = models.CharField(max_length = 30)
	scale = models.IntegerField()
	description = models.CharField(max_length = 200)	