from django.db import models

class UserModel(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    salt = models.CharField(max_length=64, blank=True)
    hashed_pwd = models.TextField(blank=True)