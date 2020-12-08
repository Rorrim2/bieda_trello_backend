from skeleton.utils.jwt_utils import get_user_by_context
from django.core import exceptions
from graphene_django import DjangoObjectType
from skeleton.activities.model import ActivityModel, ActivityTypeEnum
from skeleton.users.model import UserModel
from skeleton.cards.model import CardModel
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

	def resolve_activitys(self, info: ResolveInfo, **kwargs):
		print(info.path)
		return ActivityModel.objects.all()

	def resolve_activity(self, info: ResolveInfo, **kwargs):
		print(info.path)
		return ActivityModel.objects.filter(id=id).get()


class CreateActivity(graphene.Mutation):
	activity = graphene.Field(ActivityType)

	class Arguments:
		user_id = graphene.String(required=True)
		card_id = graphene.String(required=True)
		content = graphene.String(required=True)
		type_val = graphene.Int(required=False)
		created_on = graphene.String(required=False)

	def mutate(self, 
				info: ResolveInfo,
				user_id: str, 
				card_id: str, 
				content: str, 
				**kwargs):
		user = get_user_by_context(info.context)
		type_val = kwargs.get('type_val', None)
		created_on = kwargs.get('created_on', None)
		type_val = type_val if type_val is not None else ActivityTypeEnum.ACTIVITY_LOG_VAL
		if not UserModel.objects.filter(id=user_id).exists():
			return exceptions.ObjectDoesNotExist("Provided user does not exist")
		if not CardModel.objects.filter(id=card_id):
			return exceptions.ObjectDoesNotExist("Provided card does not exist")
		if not ActivityTypeEnum.is_viable_enum(type_val):
			return exceptions.FieldError("type_val is not a viable ActivityType value")


		card = CardModel.objects.get(id=card_id)
		user = UserModel.objects.get(id=user_id)
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
		user_id = graphene.String(required=True)
		card_id = graphene.String(required=True)
		activity_id = graphene.String(required=True)
		content = graphene.String(required=True)

	def mutate(self, info: ResolveInfo, user_id: str, card_id: str, activity_id: str, content: str):
		user = get_user_by_context(info.context)
		if not UserModel.objects.filter(id=user_id).exists():
			return exceptions.ObjectDoesNotExist("Provided user does not exist")
		if not CardModel.objects.filter(id=card_id).exists():
			return exceptions.ObjectDoesNotExist("Provided card does not exist")

		card = CardModel.objects.get(id=card_id)
		user = UserModel.objects.get(id=user_id)
		card.list.board.check_user(user, "User is not allowed to modify this board")

		activity = ActivityModel.objects.get(id=activity_id)
		activity.content = content
		activity.save()
		return EditActivity(activity=activity)
		

class Mutation(graphene.ObjectType):
	createactivity = CreateActivity.Field()
	editactivity = EditActivity.Field()