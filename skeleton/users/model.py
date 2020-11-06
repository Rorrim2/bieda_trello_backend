from django.contrib.auth.models import AbstractUser
from django.db import models
from ..utils import crypto

class UserModel(AbstractUser):
    name = models.CharField(max_length=100) 
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    salt = models.CharField(max_length=64)
    hashed_pwd = models.TextField()
    is_superuser = models.BooleanField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']

    def set_salt(self):
        self.salt = crypto.generate_salt()

    def set_password(self, password: str):
        if self.salt in [None, '']:
            self.set_salt()
        self.hashed_pwd = crypto.hash_passwd(self.salt, password)

    def check_password(self, raw_password: str):
        return crypto.validate_passwd(self.salt, raw_password, self.hashed_pwd)