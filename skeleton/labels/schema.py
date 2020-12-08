from skeleton.utils.jwt_utils import get_user_by_context
from django.core import exceptions
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from skeleton.labels.model import LabelModel
from skeleton.boards.model import BoardModel
import graphene

class LabelType(DjangoObjectType):

	class Meta:
		model = LabelModel
		interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
	labels = graphene.List(LabelType)
	label = graphene.Field(LabelType, id=graphene.String())

	def resolve_labels(self, info: ResolveInfo, **kwargs):
		print(info.path)
		return LabelModel.objects.all()

	def resolve_label(self, info: ResolveInfo, **kwargs):
		print(info.path)
		return LabelModel.objects.filter(id=id).get()


class CreateLabel(graphene.Mutation):
	label = graphene.Field(LabelType)

	class Arguments:
		name = graphene.String(required=False)
		color = graphene.String(required=True)
		board_id = graphene.String(required=True)

	def mutate(self, info: ResolveInfo, name: str, color: str, board_id: str):
		user = get_user_by_context(info.context)
		if not BoardModel.objects.filter(id=board_id).exists():
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board = BoardModel.objects.get(id=board_id)
		board.check_user(user, "User is not allowed to modify this board")

		label = LabelModel(name=name, color=color, board=board)
		label.save()

		return CreateLabel(label=label)


class EditLabel(graphene.Mutation):
	label = graphene.Field(LabelType)

	class Arguments:
		name = graphene.String(required=False)
		color = graphene.String(required=False)
		label_id = graphene.String(required=True)

	def mutate(self, info: ResolveInfo, name: str, color: str, label_id: str):
		user = get_user_by_context(info.context)
		if not LabelModel.objects.filter(id=label_id).exists():
			raise exceptions.ObjectDoesNotExist("Provided label does not exist")

		label = LabelModel.objects.get(id=label_id)
		board = label.board

		if board is None:
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board.check_user(user, "User is not allowed to modify this board")

		label.color = color if color is not None else label.color
		label.name = name if name is not None else label.name

		label.save()

		return EditLabel(label=label)

class DeleteLabel(graphene.Mutation):
	success = graphene.Boolean()

	class Arguments:
		label_id = graphene.String(required=True)

	def mutate(self, info: ResolveInfo, label_id: str):
		user = get_user_by_context(info.context)
		if not LabelModel.objects.filter(id=label_id).exists():
			raise exceptions.ObjectDoesNotExist("Provided label does not exist")
		
		label = LabelModel.objects.get(id=label_id)
		board = label.board

		if board is None:
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

			board.check_user(user, "User is not allowed to modify this board")

		label.delete()
		return DeleteLabel(success=True)


class Mutation(graphene.ObjectType):
	createlabel = CreateLabel.Field()
	editlabel = EditLabel.Field()
	deletelabel = DeleteLabel.Field()