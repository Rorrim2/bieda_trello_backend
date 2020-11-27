'''
	id: int
	name: string
	color: string
	board_id: int
'''
from django.db import models
from skeleton.boards.model import BoardModel

class LabelModel(models.Model):
	name = models.CharField(max_length=64)
	board = models.ForeignKey(to=BoardModel, on_delete=models.CASCADE, related_name='labels')
	color = models.CharField(max_length=32)