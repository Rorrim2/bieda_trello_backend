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
from skeleton.labels.model import LabelModel

class CardModel(models.Model):
	title = models.CharField(max_length=255)
	description = models.CharField(max_length=255, default="")
	list = models.ForeignKey(to=ListModel, on_delete=models.CASCADE, related_name='cards')
	archived = models.BooleanField(blank=False, default=False)
	# I assumed it will be stored as STRING
	due_date = models.DateTimeField(default=None, blank=True, null=True)
	position_in_list = models.IntegerField()
	cover = models.CharField(max_length=255, default="")
	labels = models.ManyToManyField(to=LabelModel, default=[])

	def edit(self,
				title: str,
				description: str,
				listdb: ListModel,
				archived: bool,
				due_date: str,
				position_in_list: int,
				cover: str):
		self.title = self.title if title is None else title
		self.description = self.description if description is None else description
		self.list = self.list if listdb is None else listdb
		self.archived = self.archived if archived is None else archived
		self.due_date = self.due_date if due_date is None else due_date
		self.position_in_list = self.position_in_list if position_in_list is None else position_in_list
		self.cover = self.cover if cover is None else cover

	def copy_without_id(self):
		return CardModel(title=self.title,
							description=self.description,
							list=self.list,
							archived=self.archived,
							due_date=self.due_date,
							position_in_list=self.position_in_list,
							cover=self.cover)
