import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from graphene import relay

from skeleton.boards.model import BoardModel


class BoardType(DjangoObjectType):
    class Meta:
        model = BoardModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    board = graphene.Field(BoardType)
    boards = graphene.List(BoardType)

    def resolve_boards(self, info: ResolveInfo, **kwargs):
        return BoardModel.objects.all()
