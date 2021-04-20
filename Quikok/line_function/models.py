from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userid =models.CharField(max_length=40)
    verify =models.CharField(max_length=10)
