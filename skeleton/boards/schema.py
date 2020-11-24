import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
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

    class Arguments:
        title = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, title: str, maker_email: str):
        if UserModel.objects.filter(email=maker_email).exists():
            user = UserModel.objects.get(email=maker_email)
            board = BoardModel(title=title, background="", maker=user)
            board.save()
            return CreateNewBoard(board=board)
        return GraphQLError("Board with given id does not exist")


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
        return GraphQLError("Board with given id does not exist")


class ReopenBoard(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id:str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.reopen()
            board.save()
            return ReopenBoard(board=board)
        return GraphQLError("Board with given id does not exist")


class PermanentlyDelete(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info, board_id: str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.delete()
            return PermanentlyDelete(board=board)
        return GraphQLError("Board with given id does not exist")


class UpdateBoard(graphene.Mutation):
    board = graphene.Field(BoardType)

    class Arguments:
        board_id = graphene.String(required=True)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        background = graphene.String(required=False)

    def mutate(self, info, board_id: str, title: str, description: str, background: str):
        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            board.title = title if title is not None else board.title
            board.description = description if description is not None else board.description
            board.background = background if background is not None else board.background
            board.save()
            return UpdateBoard(board=board)
        return GraphQLError("Board with given id does not exist")


class Mutation(graphene.ObjectType):
    createnewboard = CreateNewBoard.Field()
    closeBoard = CloseBoard.Field()
    reopenBoard = ReopenBoard.Field()
    permanentlydelete = PermanentlyDelete.Field()
