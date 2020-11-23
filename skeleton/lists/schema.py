from skeleton.utils.jwt_utils import get_user_by_context
import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from django.core import exceptions
from skeleton.boards.model import BoardModel
from skeleton.lists.model import ListModel


class ListType(DjangoObjectType):
    cards = graphene.List('skeleton.cards.schema.CardType')


    class Meta:
        model = ListModel

        interfaces = (graphene.relay.Node, )

    @graphene.resolve_only_args
    def resolve_cards(self):
        return self.cards.all()


class Query(graphene.ObjectType):
    lists = graphene.List(ListType)
    list = graphene.Field(ListType, id=graphene.String())

    def resolve_lists(self, info : ResolveInfo, **kwargs):
        return ListModel.objects.all()

    def resolve_list(self, info: ResolveInfo, id: str, **kwargs):
        return ListModel.objects.filter(id=id).get()


class CreateNewList(graphene.Mutation):
    list = graphene.Field(ListType)
    success = graphene.Boolean()


    class Arguments:
        title = graphene.String(required=True)
        board_id = graphene.String(required=True)
        position_on_board = graphene.Int(required=True)

    def mutate(self, info: ResolveInfo, title: str, board_id: str, position_on_board: int):
        success = False

        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.check_user(user, "User is not allowed to modify this board")

            list = ListModel(title=title, board=board, position_on_board=position_on_board)
            list.save()
            success = True
            return CreateNewList(list=list, success=success)
        else:
            raise exceptions.ObjectDoesNotExist('Provided board does not exist')


class HideList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, list_id: str):
        if not ListModel.objects.filter(id=list_id).exists():
            raise exceptions.ObjectDoesNotExist('Provided list does not exist')

        user = get_user_by_context(info.context)
        list = ListModel.objects.get(id=list_id)
        board = list.board
        board.check_user(user, "User is not allowed to modify this board")
        list.hide()
        list.save()
        return HideList(list=list)


class UnhideList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)

    def mutate(self, info, list_id: str):
        if not ListModel.objects.filter(id=list_id).exists():
            raise exceptions.ObjectDoesNotExist('Provided list does not exist')

        user = get_user_by_context(info.context)
        list = ListModel.objects.get(id=list_id)
        board = list.board
        board.check_user(user, "User is not allowed to modify this board")
        list.unhide()
        list.save()
        return UnhideList(list=list)


class Mutation(graphene.ObjectType):
    createnewlist = CreateNewList.Field()
    hidelist = HideList.Field()
    unhidelist = UnhideList.Field()