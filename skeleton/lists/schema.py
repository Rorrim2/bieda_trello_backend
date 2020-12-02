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


class UpdateList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)
        title = graphene.String(required=False)
        position_on_board = graphene.Int(required=False)

    def mutate(self, info, list_id: str, title: str, position_on_board: int):
        if ListModel.objects.filter(id=list_id).exists():
            list = ListModel.objects.get(id=list_id)
            user = get_user_by_context(info.context)
            board = list.board
            board.check_user(user, "User is not allowed to modify this board")
            list.title = title if title is not None else list.title
            list.position_on_board = position_on_board if position_on_board is not None else list.position_on_board
            list.save()
            return UpdateList(list=list)
        return exceptions.ObjectDoesNotExist('Provided list does not exist')


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


class MoveList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)
        new_board_id = graphene.String(required=True)
        new_position_on_board = graphene.Int(required=True)

    def mutate(self, info, list_id: str, new_board_id: str, new_position_on_board: int):
        if not ListModel.objects.filter(id=list_id).exists():
            raise exceptions.ObjectDoesNotExist('Provided list does not exist')
        if not BoardModel.objects.filter(id=new_board_id).exists():
            raise exceptions.ObjectDoesNotExist('Providede new board does not exist')

        user = get_user_by_context(info.context)
        listModel = ListModel.objects.get(id=list_id)
        old_board = listModel.board
        old_board.check_user(user, "User is not allowed to modify old board")

        new_board = BoardModel.objects.get(id=new_board_id)
        new_board.check_user(user, "User is not allowed to modify new board")

        # update positions of other lists on old board
        old_position_on_board = listModel.position_on_board
        for eachList in old_board.lists.all():
            if eachList.position_on_board >= old_position_on_board:
                eachList.position_on_board = eachList.position_on_board - 1
                eachList.save()

        # if new_position_on_board is greater than number of lists already on board
        # than new_position_on_board is truncated to this number
        if new_position_on_board > len(new_board.lists):
            new_position_on_board = len(new_board.lists)

        # update positions of other lists on new board
        for eachList in new_board.lists.all():
            if eachList.position_on_board >= new_position_on_board:
                eachList.position_on_board = eachList.position_on_board + 1
                eachList.save()

        listModel.board = new_board
        listModel.position_on_board = new_position_on_board
        listModel.save()
        return MoveList(listModel)


class CopyList(graphene.Mutation):
    list = graphene.Field(ListType)

    class Arguments:
        list_id = graphene.String(required=True)

    def mutate(self, info, list_id: str):
        if not ListModel.objects.filter(id=list_id).exists():
            raise exceptions.ObjectDoesNotExist('Provided list does not exist')

        user = get_user_by_context(info.context)
        originalList = ListModel.objects.get(id=list_id)
        board = originalList.board
        board.check_user(user, "User is not allowed to modify old board")

        # update positions of other lists on board
        for eachList in board.lists.all():
            if eachList.position_on_board > originalList.position_on_board:
                eachList.position_on_board = eachList.position_on_board + 1
                eachList.save()

        copiedList = ListModel(title=originalList.title,
                               board=originalList.board,
                               position_on_board=originalList.position_on_board + 1,
                               is_hidden=originalList.is_hidden)
        copiedList.save()

        for originalCard in originalList.cards.all():
            newCard = originalCard.copy_without_id()
            newCard.list = copiedList
            newCard.save()

        return MoveList(copiedList)


class Mutation(graphene.ObjectType):
    createnewlist = CreateNewList.Field()
    hidelist = HideList.Field()
    unhidelist = UnhideList.Field()
    updatelist = UpdateList.Field()
    movelist = MoveList.Field()
    copylist = CopyList.Field()