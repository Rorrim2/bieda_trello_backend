from graphene_django import DjangoObjectType
import graphene
from graphql.execution.base import ResolveInfo
from graphql_jwt import shortcuts
from django.utils import timezone
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
        return UserModel.objects.all()


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email: str, password: str):
        user = None
        success = False
        token=''
        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            if crypto.validate_passwd(user.salt, password, user.hashed_pwd):
                token = shortcuts.get_token(user)
                success = True
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
            else:
                user = None

        return LoginUser(user=user, success=success, token=token)


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, email: str, password: str, name: str, last_name: str):
        user = None
        success = False
        token=''
        if not UserModel.objects.filter(email=email).exists():
            user = UserModel(name=name, last_name=last_name, email=email)
            user.set_salt()
            user.set_password(password)
            user.save()
            success = True
            token = shortcuts.get_token(user)

        return RegisterUser(user=user, success=success, token=token)


class Mutation(graphene.ObjectType):
    loginuser = LoginUser.Field()
    registeruser = RegisterUser.Field()
