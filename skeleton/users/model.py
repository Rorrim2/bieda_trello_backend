from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from ..utils import crypto
from django.contrib.auth.models import PermissionsMixin
import unicodedata

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
    
class UserModel(models.Model):

    last_login = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100) 
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    salt = models.CharField(max_length=64)
    hashed_pwd = models.TextField()
    is_superuser = models.BooleanField(blank=True, default=False)
    is_staff = models.BooleanField(default=False)
    is_active = True
    jwt_salt = models.CharField(max_length=64, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']

    def __str__(self):
        return self.get_username()

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    def clean(self):
        setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))

    def natural_key(self):
        return (self.get_username(),)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @classmethod
    def get_email_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return 'email'

    @classmethod
    def normalize_username(cls, username):
        return unicodedata.normalize('NFKC', username) if isinstance(username, str) else username


    def get_all_permissions(self, obj=None):
        return PermissionsMixin.get_all_permissions() if self.is_superuser else set()

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perms(self, perm_list, obj=None):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def set_salt(self):
        self.salt = crypto.generate_salt()

    def set_password(self, password: str):
        if self.salt in [None, '']:
            self.set_salt()
        self.hashed_pwd = crypto.hash_passwd(self.salt, password)

    def check_password(self, raw_password: str):
        return crypto.validate_passwd(self.salt, raw_password, self.hashed_pwd)

