import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo

from skeleton.cards.model import CardModel
from skeleton.lists.model import ListModel


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


class CreateCard(graphene.Mutation):
    card = graphene.Field(CardType)
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        email = graphene.String(required=True)
        list_id = graphene.String(required=True)

    def mutate(self, info, title: str, email: str, list_id: str):
        pass


class EditCard(graphene.Mutation):
    card = graphene.Field(CardType)
    success = graphene.Boolean()

    class Arguments:
        card_id = graphene.String(required=True)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        list_id = graphene.String(required=False)
        archived = graphene.Boolean(required=False)
        due_date = graphene.String(required=False)
        position_in_list = graphene.Int(required=False)
        cover = graphene.String(required=False)

    def mutate(self,
               info,
               card_id: str,
               **kwargs):
        title = kwargs.get('title', None)
        description = kwargs.get('description', None)
        list_id = kwargs.get('list_id', None)
        archived = kwargs.get('archived', None)
        due_date = kwargs.get('due_date', None)
        position_in_list = kwargs.get('position_in_list', None)
        cover = kwargs.get('cover', None)

        if CardModel.objects.filter(id=card_id).exists():
            card = CardModel.objects.get(id=card_id)
            listdb = None
            if list_id is not None and ListModel.objects().filter(id=list_id).exists():
                listdb = ListModel.objects().get(id=list_id)
            card.edit(title=title,
                      description=description,
                      listdb=listdb,
                      archived=archived,
                      due_date=due_date,
                      position_in_list=position_in_list,
                      cover=cover,
                      )
            card.save()
            return EditCard(card=card, success=True)
        return EditCard(card=None, success=False)


class Mutation(graphene.ObjectType):
    createcard = CreateCard.Field()
    editcard = EditCard.Field()