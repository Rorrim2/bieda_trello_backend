# Register your models here.
from django.contrib import admin

from skeleton.models import UserModel, BoardModel, ListModel, CardModel

admin.register(UserModel)
admin.register(BoardModel)
admin.register(ListModel)
admin.register(CardModel)
admin.site.register(UserModel)
admin.site.register(BoardModel)
admin.site.register(ListModel)
admin.site.register(CardModel)