from skeleton.utils import map_id
from skeleton.utils.jwt_utils import get_user_by_context
from django.core import exceptions
from graphene_django import DjangoObjectType
from skeleton.activities.model import ActivityModel, ActivityTypeEnum
from skeleton.users.model import UserModel
from skeleton.cards.model import CardModel
from skeleton.boards.model import BoardModel
from skeleton.lists.model import ListModel
from graphql.execution.base import ResolveInfo

import graphene
from datetime import datetime

class ActivityType(DjangoObjectType):

	class Meta:
		model = ActivityModel
		interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
	activitys = graphene.List(ActivityType)
	activity = graphene.Field(ActivityType, id=graphene.String())
	activitysByUser = graphene.List(ActivityType, userId=graphene.String())
	activitysByCard = graphene.List(ActivityType, cardId=graphene.String())
	activitysByBoard = graphene.List(ActivityType, boardId=graphene.String())


	def resolve_activitys(self, info: ResolveInfo, **kwargs):
		print(info.path)
		user = get_user_by_context(info.context)
		return ActivityModel.objects.all()

	def resolve_activity(self, info: ResolveInfo, id: str, **kwargs):
		print(info.path)
		user = get_user_by_context(info.context)
		return ActivityModel.objects.filter(id=map_id(id)).get()

	def resolve_activitysByUser(self, info: ResolveInfo, **kwargs):
		user = get_user_by_context(info.context)
		return ActivityModel.objects.filter(user=user)

	def resolve_activitysByCard(self, info: ResolveInfo, cardId: str, **kwargs):
		if not CardModel.objects.filter(id=map_id(cardId)).exists():
			return exceptions.ObjectDoesNotExist("Provided card does not exist")
		user = get_user_by_context(info.context)

		card = CardModel.objects.get(id=map_id(cardId))
		card.list.board.check_user(user, "User is not allowed to even LOOK at this board. Get him outa here")
		return ActivityModel.objects.filter(card=card)

	def resolve_activitysByBoard(self, info: ResolveInfo, boardId: str, **kwargs):
		if not BoardModel.objects.filter(id=map_id(boardId)).exists():
			return exceptions.ObjectDoesNotExist("Provided board does not exist")

		user = get_user_by_context(info.context)
		# *sniff* *sniff* reeks of newbie maybe will change it later
		# sick, probably not :)
		board = BoardModel.objects.get(id=map_id(boardId))
		board.check_user(user, "User is not allowed to even LOOK at this board. Get him outa here")
		activitiesQuerySet = ActivityModel.objects.filter(card=None)
		lists = ListModel.objects.get(board=board)
		for eachList in lists:
			cards = CardModel.objects.filter(list=eachList)
			for card in cards:
				activitiesQuerySet.union(ActivityModel.objects.filter(card=card))
		
		return activitiesQuerySet


class CreateActivity(graphene.Mutation):
	activity = graphene.Field(ActivityType)

	class Arguments:
		card_id = graphene.String(required=True)
		content = graphene.String(required=True)
		type_val = graphene.Int(required=False)
		created_on = graphene.String(required=False)

	def mutate(self, 
				info: ResolveInfo,
				card_id: str, 
				content: str, 
				**kwargs):
		user = get_user_by_context(info.context)
		type_val = kwargs.get('type_val', None)
		created_on = kwargs.get('created_on', None)
		type_val = type_val if type_val is not None else ActivityTypeEnum.ACTIVITY_LOG_VAL
		if not CardModel.objects.filter(id=map_id(card_id)):
			return exceptions.ObjectDoesNotExist("Provided card does not exist")
		if not ActivityTypeEnum.is_viable_enum(type_val):
			return exceptions.FieldError("type_val is not a viable ActivityType value")


		card = CardModel.objects.get(id=map_id(card_id))
		card.list.board.check_user(user, "User is not allowed to modify this board")
		if created_on is None:
			activity = ActivityModel(
				card=card, 
				user=user, 
				content=content, 
				type=type_val,
				)
		else:
			activity = ActivityModel(
				card=card, 
				user=user, 
				content=content, 
				created_on=created_on,
				type=type_val,
				)
		activity.save()
		return CreateActivity(activity=activity)


class EditActivity(graphene.Mutation):
	activity = graphene.Field(ActivityType)

	class Arguments:
		activity_id = graphene.String(required=True)
		content = graphene.String(required=True)

	def mutate(self, info: ResolveInfo, activity_id: str, content: str):
		user = get_user_by_context(info.context)

		activity = ActivityModel.objects.get(id=map_id(activity_id))
		activity.card.list.board.check_user(user, "User is not allowed to modify this board")

		activity.content = content
		activity.save()
		return EditActivity(activity=activity)
		

class Mutation(graphene.ObjectType):
	createactivity = CreateActivity.Field()
	editactivity = EditActivity.Field()