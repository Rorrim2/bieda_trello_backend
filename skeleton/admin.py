# Register your models here.
from django.contrib import admin

from skeleton.boards.model import BoardModel
from skeleton.lists.model import ListModel
from skeleton.models import UserModel

admin.register(UserModel)
admin.register(BoardModel)
admin.register(ListModel)
admin.site.register(UserModel)
admin.site.register(BoardModel)
admin.site.register(ListModel)