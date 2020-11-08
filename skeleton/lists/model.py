'''
    id: int
    title: str
    board_id: int
'''
from django.db import models

from skeleton.boards.model import BoardModel


class ListModel(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey(BoardModel, on_delete=models.CASCADE,)
