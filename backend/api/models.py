from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=100)
    recept_number = models.CharField(max_length=100,unique=True)
    bank_balance = models.IntegerField(blank=True,default = 5000)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    warning = models.IntegerField(blank = True,default = 0)
    block = models.BooleanField(blank=True,default=False)
    username=''
    USERNAME_FIELD='email'

    REQUIRED_FIELDS =[]

    def save(self, *args, **kwargs):
        if self.warning == 2:
            self.block = True 
        super().save(*args, **kwargs)

class Stock(models.Model):
    stock_quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    operations = models.CharField(max_length=100)
    total_amount = models.IntegerField()
    stock_name = models.CharField(max_length=100)
    quantity = models.IntegerField()

