import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo

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