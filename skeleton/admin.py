# Register your models here.
from django.contrib import admin

from skeleton.boards.model import BoardModel
from skeleton.models import UserModel

admin.register(UserModel)
admin.register(BoardModel)
admin.site.register(UserModel)
admin.site.register(BoardModel)