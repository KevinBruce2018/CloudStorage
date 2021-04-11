from django.db import models
from django.db.models.base import Model
from django.db.models.fields import DateField
import django.utils.timezone as timezone

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=64)
    status = models.IntegerField()
    authority = models.IntegerField()
    email = models.CharField(max_length=100)

class FileMessage(models.Model):
    name = models.CharField(max_length=128)
    size = models.IntegerField()
    path = models.CharField(max_length=200)
    auther = models.CharField(max_length=20)
    secret_key_one = models.CharField(max_length=300)
    secret_key_two = models.CharField(max_length=300)
    secret_index = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    hashcode = models.CharField(max_length=32)

class Log(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=15)
    username = models.CharField(max_length=20)
    source = models.CharField(max_length=200)
    operation = models.CharField(max_length=20)
    status = models.CharField(max_length=30)
    result = models.CharField(max_length=10)