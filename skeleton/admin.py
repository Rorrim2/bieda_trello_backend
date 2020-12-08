# Register your models here.
from django.contrib import admin

from skeleton.models import UserModel, BoardModel, ListModel, CardModel, JTIModel, LabelModel

admin.register(UserModel)
admin.register(BoardModel)
admin.register(ListModel)
admin.register(CardModel)
admin.register(JTIModel)
admin.register(LabelModel)
admin.site.register(UserModel)
admin.site.register(BoardModel)
admin.site.register(ListModel)
admin.site.register(CardModel)
admin.site.register(JTIModel)
admin.site.register(LabelModel)
