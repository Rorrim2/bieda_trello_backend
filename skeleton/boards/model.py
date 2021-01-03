from skeleton.users.model import UserModel
from django.core import exceptions
'''
    id: int
    # necessary to create
    title: str
    maker_id: int
    # optional
    background: str
    # additive after
    description: str
    is_closed: bool
    is_visible: bool
'''
from django.db import models


class BoardModel(models.Model):
    title = models.CharField(max_length=255)
    maker = models.ForeignKey(to=UserModel, on_delete=models.SET_DEFAULT, 
                              default=None, related_name='owns')
    is_closed = models.BooleanField(blank=False, default=False)
    is_visible = models.BooleanField(blank=True, default=True)
    description = models.TextField()
    background = models.CharField(max_length=255)
    users = models.ManyToManyField(UserModel, default=[], related_name='boards')
    admins = models.ManyToManyField(UserModel, default=[], related_name='manages')

    def close(self):
        self.is_closed = True

    def reopen(self):
        self.is_closed = False

    def check_user(self, user, message: str):
        if (user not in self.users.all() and
            user not in self.admins.all() and
            user is not self.maker):
                raise exceptions.PermissionDenied(message)