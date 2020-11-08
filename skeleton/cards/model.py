'''
 id: int
 title: str
 description: str
 list_id: int
 archived: bool
 due_date: datetime
 position_in_list: int
 cover: str
'''
from django.db import models

from skeleton.lists.model import ListModel


class CardModel(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, default="")
    list = models.ForeignKey(to=ListModel, on_delete=models.CASCADE,)
    archived = models.BooleanField(blank=False, default=False)
    # I assumed it will be stored as STRING
    due_date = models.DateTimeField(default=None, blank=True, null=True)
    position_in_list = models.IntegerField()
    cover = models.CharField(max_length=255, default="")
