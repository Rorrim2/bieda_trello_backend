'''
    id: int
    title: str
    board_id: int
'''
from django.db import models


class ListModel(models.Model):
    title = models.CharField(max_length=255)
    board_id = models.IntegerField()
