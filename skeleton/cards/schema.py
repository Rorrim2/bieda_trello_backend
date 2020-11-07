import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo

from skeleton.cards.model import CardModel


class CardType(DjangoObjectType):
    class Meta:
        model = CardModel

        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    card = graphene.Field(CardType)
    cards = graphene.List(CardType)

    def resolve_cards(self, info: ResolveInfo, **kwargs):
        print(info.path)
        return CardModel.objects.all()