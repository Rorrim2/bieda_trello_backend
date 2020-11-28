from skeleton.utils.jwt_utils import get_user_by_context
from django.core import exceptions
from graphene_django import DjangoObjectType
from skeleton.activities.model import ActivityModel
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
		type_val = graphene.Int(required=False)
		content = graphene.String(required=True)
		created_on = graphene.String(required=False)

	def mutate(self, 
				user_id: str, 
				card_id: str, 
				type_val: int, 
				content: str, 
				created_on: str):
		if not UserModel.objects.filter(id=user_id).exists():
			return exceptions.ObjectDoesNotExist("Provided user does not exist")
		if not CardModel.objects.filter(id=card_id):
			return exceptions.ObjectDoesNotExist("Provided card does not exist")
		if not ActivityModel.ActivityType.is_viable_enum(type_val):
			return exceptions.FieldError("type_val is not a viable ActivityType value")

		created_on_date = datetime.strptime(created_on, ActivityModel.date_storage_format)

		card = CardModel.objects.get(id=card_id)
		user = CardModel.objects.get(id=user_id)
		card.list.board.check_user(user, "User is not allowed to modify this board")
		creation_date = created_on_date if created_on_date is not None else datetime.now()
		activity = ActivityModel(card=card, 
			user=user, 
			created_on=creation_date, 
			content=content, 
			type=ActivityType.vals_tuple(type_val),
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

	def mutate(self, user_id: str, card_id: str, activity_id: str, content: str):
		if not UserModel.objects.filter(id=user_id).exists():
			return exceptions.ObjectDoesNotExist("Provided user does not exist")
		if not CardModel.objects.filter(id=card_id).exists():
			return exceptions.ObjectDoesNotExist("Provided card does not exist")

		card = CardModel.objects.get(id=card_id)
		user = CardModel.objects.get(id=user_id)
		card.list.board.check_user(user, "User is not allowed to modify this board")

		activity = ActivityModel.objects.get(id=activity_id)
		activity.content = content
		activity.save()
		return EditActivity(activity=activity)
		

class Mutation(graphene.ObjectType):
	createactivity = CreateActivity.Field()
	editactivity = EditActivity.Field()