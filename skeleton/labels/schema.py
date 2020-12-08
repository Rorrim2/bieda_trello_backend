from skeleton.utils.jwt_utils import get_user_by_context
from django.core import exceptions
from graphene_django import DjangoObjectType
<<<<<<< HEAD
from graphql.execution.base import ResolveInfo
=======
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26
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
<<<<<<< HEAD
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board = BoardModel.objects.get(id=board_id)
		board.check_user(user, "User is not allowed to modify this board")
=======
            raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board = BoardModel.objects.get(id=board_id)
        board.check_user(user, "User is not allowed to modify this board")
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26

		label = LabelModel(name=name, color=color, board=board)
		label.save()

		return CreateLabel(label=label)


class EditLabel(graphene.Mutation):
	label = graphene.Field(LabelType)

	class Arguments:
		name = graphene.String(required=False)
		color = graphene.String(required=False)
		label_id = graphene.String(required=True)

<<<<<<< HEAD
	def mutate(self, info: ResolveInfo, name: str, color: str, label_id: str):
=======
	def mutate(self, info: ResolveInfo, name: str, color: str, lable_id: str):
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26
		user = get_user_by_context(info.context)
		if not LabelModel.objects.filter(id=label_id).exists():
			raise exceptions.ObjectDoesNotExist("Provided label does not exist")

<<<<<<< HEAD
		label = LabelModel.objects.get(id=label_id)
		board = label.board

		if board is None:
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board.check_user(user, "User is not allowed to modify this board")
=======
		label = LabelModel.objects.get(id=lable_id)
		board = label.board

		if board is None:
            raise exceptions.ObjectDoesNotExist("Provided board does not exist")

        board.check_user(user, "User is not allowed to modify this board")
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26

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
<<<<<<< HEAD
			raise exceptions.ObjectDoesNotExist("Provided board does not exist")

		board.check_user(user, "User is not allowed to modify this board")
=======
            raise exceptions.ObjectDoesNotExist("Provided board does not exist")

        board.check_user(user, "User is not allowed to modify this board")
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26

		label.delete()
		return DeleteLabel(success=True)


<<<<<<< HEAD
class Mutation(graphene.ObjectType):
=======
class Mutation(graphene.Mutation):
>>>>>>> d7455d820130c12761de80b4aefb776d8d7c9e26
	createlabel = CreateLabel.Field()
	editlabel = EditLabel.Field()
	deletelabel = DeleteLabel.Field()