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
from datetime import datetime
from django.core import exceptions

class ActivityTypeEnum():
	ACTIVITY_LOG_VAL = 1
	COMMENT_VAL = 2
	CHECKLIST_VAL = 3
	ATTACHMENT_VAL = 4

	ACTIVITY_LOG_TYPE = (ACTIVITY_LOG_VAL, ('Used for logging additions, deletions and modifications on card'))
	COMMENT_TYPE = (COMMENT_VAL, ('Comment'))
	CHECKLIST_TYPE = (CHECKLIST_VAL, ('Checklist, content contains points and is_checked value'))
	ATTACHMENT_TYPE = (ATTACHMENT_VAL, ('Attachements, do not know if it will even be used though'))

	TYPES_DICT = {
		ACTIVITY_LOG_VAL: ACTIVITY_LOG_TYPE,
		COMMENT_VAL: COMMENT_TYPE,
		CHECKLIST_VAL: CHECKLIST_TYPE,
		ATTACHMENT_VAL: ATTACHMENT_TYPE
	}

	TYPES = (
		ACTIVITY_LOG_TYPE,
		COMMENT_TYPE,
		CHECKLIST_TYPE,
		ATTACHMENT_TYPE
	)

	@staticmethod
	def is_viable_enum(value: int):
		return any(value in item for item in ActivityTypeEnum.TYPES)
	
	@staticmethod
	def vals_tuple(value: int):
		if ActivityTypeEnum.is_viable_enum(value):
			return ActivityTypeEnum.TYPES_DICT[value]
		return exceptions.FieldError("type_val is not a viable ActivityTypeEnum value")

class ActivityModel(models.Model):
	date_storage_format = '%d:%m%y:%H:%M:%S'

	card = models.ForeignKey(to=CardModel, on_delete=models.CASCADE, related_name='activities')
	user = models.ForeignKey(to=CardModel, on_delete=models.CASCADE)
	created_on = models.DateTimeField(default=datetime.now)
	content = models.CharField(max_length=1024)
	type = models.IntegerField(choices=ActivityTypeEnum.TYPES)

