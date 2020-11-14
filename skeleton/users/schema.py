from graphene_django import DjangoObjectType
import graphene
from graphql.execution.base import ResolveInfo
from graphql_jwt import shortcuts
from django.utils import timezone
from django.http import HttpRequest
from ..utils import crypto
from .model import UserModel


# this file is something like top-level urls.py
# where we define our "endpoints"
class UserType(DjangoObjectType):
    class Meta:
        model = UserModel
        fields = ("id", "name", "last_name", "email")
        
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType)

    def resolve_users(self, info: ResolveInfo, **kwargs):
        print(info.path)
        print(info.context.headers)
        return UserModel.objects.all()


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, email: str, password: str):
        user = None
        success = False
        token=''
        refreshtkn = ''
        print(info.context.headers)

        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            if crypto.validate_passwd(user.salt, password, user.hashed_pwd):
                token = shortcuts.get_token(user)
                refreshtkn = shortcuts.create_refresh_token(user)
                success = True
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
            else:
                user = None

        return LoginUser(user=user, success=success, token=token, refresh_token=refreshtkn)


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        refresh_token = graphene.String(required=True)
        

    def mutate(self, info: ResolveInfo, refresh_token: str):
        jwt_token = info.context.headers['Authorization'].replace('Bearer ','')

        

class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, email: str, password: str, name: str, last_name: str):
        user = None
        success = False
        token = ''
        refreshtkn = ''
        
        if not UserModel.objects.filter(email=email).exists():
            user = UserModel(name=name, last_name=last_name, email=email)
            user.set_salt()
            user.set_password(password)
            user.save()
            success = True
            token = shortcuts.get_token(user)
            refreshtkn = shortcuts.create_refresh_token(user)

        return RegisterUser(user=user, success=success, token=token, refresh_token=refreshtkn)


class Mutation(graphene.ObjectType):
    loginuser = LoginUser.Field()
    registeruser = RegisterUser.Field()
