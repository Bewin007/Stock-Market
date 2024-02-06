from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=100)
    recept_number = models.CharField(max_length=100,unique=True)
    bank_balance = models.IntegerField()
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    
    username=''
    USERNAME_FIELD='email'

    REQUIRED_FIELDS =[]


class Stock(models.Model):
    stock_quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)


class Log(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    action = models.CharField(max_length=100)
    price = models.IntegerField()
    stock_name = models.CharField(max_length=100)
    volume = models.IntegerField()