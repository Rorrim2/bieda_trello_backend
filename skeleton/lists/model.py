'''
    id: int
    title: str
    board_id: int
    is_hidden: bool
'''
from django.db import models

from skeleton.boards.model import BoardModel


class ListModel(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey(BoardModel, on_delete=models.CASCADE, related_name='lists')
    position_on_board = models.IntegerField()
    is_hidden = models.BooleanField(default=False)

    def hide(self):
        self.is_hidden = True

    def unhide(self):
        self.is_hidden = False
