from skeleton.utils import map_id
from skeleton.utils.jwt_utils import get_user_by_context
import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from django.core import exceptions
from skeleton.cards.model import CardModel
from skeleton.lists.model import ListModel
from skeleton.activities.model import ActivityModel, ActivityTypeEnum
from datetime import datetime

class CardType(DjangoObjectType):

    labels = graphene.List('skeleton.labels.schema.LabelType')
    activities = graphene.List('skeleton.activities.schema.ActivityType')

    @graphene.resolve_only_args
    def resolve_activities(self):
        return self.activities.all()

    @graphene.resolve_only_args
    def resolve_labels(self):
        return self.labels.all()

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
        return CardModel.objects.filter(id=map_id(id)).get()


class CreateCard(graphene.Mutation):

    card = graphene.Field(CardType)
    success = graphene.Boolean()


    class Arguments:
        title = graphene.String(required=True)
        list_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, title: str, list_id: str):
        user = get_user_by_context(info.context)
        if not ListModel.objects.filter(id=map_id(list_id)).exists(): 
            raise exceptions.ObjectDoesNotExist("Provided list does not exist")

        list_db = ListModel.objects.filter(id=map_id(list_id)).get()
        list_db.board.check_user(user, "User is not allowed to modify this board")
        
        lists_cards = CardModel.objects.filter(list=list_db)

        card = CardModel(list=list_db, title=title, position_in_list=len(lists_cards))
        card.save()

        activityContent = user.name + " " + user.last_name + " created card and added it to list " + card.list.title
        activity = ActivityModel(card=card, 
            user=user,
            content=activityContent, 
            type=ActivityTypeEnum.ACTIVITY_LOG_VAL)
        activity.save()
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
        # user = get_user_by_context(info.context)
        title = kwargs.get('title', None)
        description = kwargs.get('description', None)
        list_id = kwargs.get('list_id', None)
        archived = kwargs.get('archived', None)
        due_date = kwargs.get('due_date', None)
        position_in_list = kwargs.get('position_in_list', None)
        cover = kwargs.get('cover', None)

        if CardModel.objects.filter(id=map_id(card_id)).exists():
            user = get_user_by_context(info.context)
            card = CardModel.objects.get(id=map_id(card_id))
            card.list.board.check_user(user, 'User have no permission to update this board')
            listdb: ListModel = None

            if list_id is not None and ListModel.objects().filter(id=map_id(list_id)).exists():
                listdb = ListModel.objects().get(id=map_id(list_id))
            elif list_id is not None:
                raise exceptions.ObjectDoesNotExist('Provided list does not exist')

            # listdb.board.check_user(user, "User is not allowed to modify this board")  
            card.edit(title=title,
                      description=description,
                      listdb=listdb,
                      archived=archived,
                      due_date=due_date,
                      position_in_list=position_in_list,
                      cover=cover,
                      )
            activityContent = user.name + " " + user.last_name + " edited card in list " + card.list.title
            activity = ActivityModel(card=card, 
                user=user, 
                content=activityContent, 
                type=ActivityTypeEnum.ACTIVITY_LOG_VAL)
            activity.save()
            card.save()
            return EditCard(card=card, success=True)
        else:
            raise exceptions.ObjectDoesNotExist("Provided card does not exist")


class DeleteCard(graphene.Mutation):
    card = graphene.Field(CardType)
    success = graphene.Boolean()

    class Arguments:
        card_id = graphene.String(required=True)

    def mutate(self,
               info: ResolveInfo,
               card_id: str):
        user = get_user_by_context(info.context)

        if CardModel.objects.filter(id=map_id(card_id)).exists():
            card = CardModel.objects.get(id=map_id(card_id))
            listdb = card.list
            listdb.board.check_user(user, "User is not allowed to modify this board")
            card.delete()
            return DeleteCard(card=card, success=True)
        else:
            raise exceptions.ObjectDoesNotExist("Provided card does not exist")


class Mutation(graphene.ObjectType):
    createcard = CreateCard.Field()
    editcard = EditCard.Field()
    deletecard = DeleteCard.Field()