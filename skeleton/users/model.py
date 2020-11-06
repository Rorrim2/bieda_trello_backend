from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from ..utils import crypto
from django.contrib.auth.models import PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, email: str, password: str, name: str, last_name: str, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email: str, password: str, name: str, last_name: str, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, name, last_name, **extra_fields)

    def create_superuser(self, email: str, password: str, name: str, last_name: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, name, last_name, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(email=username)
    
class UserModel(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100) 
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    salt = models.CharField(max_length=64)
    hashed_pwd = models.TextField()
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']

    class Admin:
        manager = UserManager()

    def set_salt(self):
        self.salt = crypto.generate_salt()

    def set_password(self, password: str):
        if self.salt in [None, '']:
            self.set_salt()
        self.hashed_pwd = crypto.hash_passwd(self.salt, password)

    def check_password(self, raw_password: str):
        return crypto.validate_passwd(self.salt, raw_password, self.hashed_pwd)

