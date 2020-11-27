'''
	id: int
	card_id : int
	user_id : int
	created_on : datetime
	content : string <- most likely JSON
	type : int <- enum

		type enum:
			comment
			activity <- logs
			attachment
			checklist

'''

from django.db import models
from skeleton.cards.model import CardModel

class ActivityModel(models.Model):
	card = models.ForeignKey(to=CardModel, on_delete=models.CASCADE, related_name='activities')
	user = models.ForeignKey(to=CardModel, on_delete=models.CASCADE)
	created_on = models.DateTimeField()
	content = models.CharField(max_length=1024)
	type = models.IntegerField(choices=ActivityType.choices=)

	class ActivityType():
		ACTIVITY_LOG = 1
		COMMENT = 2
		CHECKLIST = 3
		ATTACHMENT = 4

		TYPES = (
			(ACTIVITY_LOG, _('Used for logging additions, deletions and modifications on card')),
			(COMMENT, _('Comment')),
			(CHECKLIST, _('Checklist, content contains points and is_checked value')),
			(ATTACHMENT, _('Attachements, do not know if it will even be used though'))
		)