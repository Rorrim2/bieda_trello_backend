from skeleton.utils.jwt_utils import get_user_by_context
import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from django.core import exceptions
from skeleton.cards.model import CardModel
from skeleton.lists.model import ListModel


class CardType(DjangoObjectType):


    class Meta:
        model = CardModel
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    card = graphene.Field(CardType, id=graphene.String())
    cards = graphene.List(CardType)

    def resolve_cards(self, info: ResolveInfo, **kwargs):
        print(info.path)
        return CardModel.objects.all()

    def resolve_card(self, info: ResolveInfo, **kwargs):
        print(info.path)
        return CardModel.objects.filter(id=id).get()


class CreateCard(graphene.Mutation):

    card = graphene.Field(CardType)
    success = graphene.Boolean()


    class Arguments:
        title = graphene.String(required=True)
        list_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, title: str, list_id: str):
        user = get_user_by_context(info.context)
        if not ListModel.objects.filter(id=list_id).exists(): 
            raise exceptions.ObjectDoesNotExist("Provided list does not exist")

        list_db = ListModel.objects.filter(id=list_id).get()
        list_db.board.check_user(user)

        card = CardModel(list=list_db, title=title, position_in_list=len(list_db.cards))
        return CreateCard(card=card, success=True)
        

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
               info: ResolveInfo,
               card_id: str,
               **kwargs):
        user = get_user_by_context(info.context)
        title = kwargs.get('title', None)
        description = kwargs.get('description', None)
        list_id = kwargs.get('list_id', None)
        archived = kwargs.get('archived', None)
        due_date = kwargs.get('due_date', None)
        position_in_list = kwargs.get('position_in_list', None)
        cover = kwargs.get('cover', None)

        if CardModel.objects.filter(id=card_id).exists():
            card = CardModel.objects.get(id=card_id)
            listdb: ListModel = None

            if list_id is not None and ListModel.objects().filter(id=list_id).exists():
                listdb = ListModel.objects().get(id=list_id)
            elif list_id is not None:
                raise exceptions.ObjectDoesNotExist('Provided list does not exist')

            listdb.board.check_user(user)  
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
        else:
            raise exceptions.ObjectDoesNotExist("Provided card does not exist")


class Mutation(graphene.ObjectType):
    createcard = CreateCard.Field()
    editcard = EditCard.Field()