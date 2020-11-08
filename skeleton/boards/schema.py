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

    def mutate(self, info, title: str, email: str):
        success = False
        user = None
        board = None
        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            board = BoardModel(title=title, background="", maker=user)
            board.save()
            success = True
        else:
            board = BoardModel(title=None, background=None, maker=None)
        return CreateNewBoard(board=board, success=success)


class Close(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.close()
            board.save()
        return Close(board_id=board_id)


class Reopen(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.reopen()
            board.save()
        return Reopen()


class PermanentlyDelete(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            BoardModel.objects.get(id=board_id).delete()
        return Reopen()


class Mutation(graphene.ObjectType):
    createnewboard = CreateNewBoard.Field()
    close = Close.Field()
    reopen = Reopen.Field()
    permanentlydelete = PermanentlyDelete.Field()
