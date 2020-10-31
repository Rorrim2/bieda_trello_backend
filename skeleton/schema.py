from graphene_django import DjangoObjectType
import graphene
from graphql.execution.base import ResolveInfo

from .models import UserModel

# this file is something like top-level urls.py
# where we define our "endpoints"
class UserType(DjangoObjectType):
    class Meta:
        model = UserModel
        fields = ("id","name", "last_name")
        filter_fields = {'id': ['exact']}
        interfaces = (graphene.relay.Node, )
        
class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info: ResolveInfo, **kwargs):
        print(info.path)
        return UserModel.objects.all()

schema = graphene.Schema(query=Query)