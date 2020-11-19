import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo

from skeleton.boards.model import BoardModel
from skeleton.lists.model import ListModel


class ListType(DjangoObjectType):
    class Meta:
        model = ListModel

        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    lists = graphene.List(ListType)
    list = graphene.Field(ListType)

    def resolve_lists(self, info : ResolveInfo, **kwargs):
        return ListModel.objects.all()


class CreateNewList(graphene.Mutation):
    list = graphene.Field(ListType)
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        board_id = graphene.String(required=True)
        position_on_board = graphene.Int(required=True)

    def mutate(self, info, title: str, board_id: str, position_on_board: int):
        success = False
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            list = ListModel(title=title, board=board, position_on_board=position_on_board)
            list.save()
            success = True
            return CreateNewList(list=list, success=success)
        return CreateNewList(list=None, success=success)


class HideList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)

    def mutate(self, info, list_id: str):
        list = ListModel.objects.get(id=list_id)
        list.hide()
        list.save()
        return HideList(list=list)


class UnhideList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)

    def mutate(self, info, list_id: str):
        list = ListModel.objects.get(id=list_id)
        list.unhide()
        list.save()
        return UnhideList(list=list)


class Mutation(graphene.ObjectType):
    createnewlist = CreateNewList.Field()
    hidelist = HideList.Field()
    unhidelist = UnhideList.Field()