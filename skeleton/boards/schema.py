import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from graphene import relay

from skeleton.boards.model import BoardModel
from skeleton.users.model import UserModel


class BoardType(DjangoObjectType):
    class Meta:
        model = BoardModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    board = graphene.Field(BoardType)
    boards = graphene.List(BoardType)

    def resolve_boards(self, info: ResolveInfo, **kwargs):
        return BoardModel.objects.all()


class CreateNewBoard(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, title: str, maker_email: str):
        success = False
        user = None
        board = None
        if UserModel.objects.filter(email=maker_email).exists():
            user = UserModel.objects.get(email=maker_email)
            board = BoardModel(title=title, background="", maker=user)
            board.save()
            success = True
        else:
            board = BoardModel(title=None, background=None, maker=None)
        return CreateNewBoard(board=board, success=success)


class CloseBoard(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.close()
            board.save()
        return CloseBoard(board=board)


class ReopenBoard(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.reopen()
            board.save()
        return ReopenBoard(board=board)


class PermanentlyDelete(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        success = False
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.delete()
            success = True
            return PermanentlyDelete(board=board, success=success)
        return PermanentlyDelete(board=None, success=success)


class Mutation(graphene.ObjectType):
    createnewboard = CreateNewBoard.Field()
    closeBoard = CloseBoard.Field()
    reopenBoard = ReopenBoard.Field()
    permanentlydelete = PermanentlyDelete.Field()
