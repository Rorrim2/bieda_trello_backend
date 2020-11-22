from graphene_django import DjangoObjectType
import graphene
from graphql.execution.base import ResolveInfo
from graphql_jwt import shortcuts
from django.utils import timezone
from ..utils import crypto, jwt_utils
from .model import UserModel
from django.core import exceptions
from graphql.error import GraphQLError


class UserType(DjangoObjectType):
    
    boards = graphene.List('skeleton.boards.schema.BoardType')
    owns = graphene.List('skeleton.boards.schema.BoardType')
    manages = graphene.List('skeleton.boards.schema.BoardType')

    @graphene.resolve_only_args
    def resolve_boards(self):
        return set(list(self.boards.all()) + list(self.owns.all()) + list(self.manages.all()))

    class Meta:
        model = UserModel
        fields = ("id", "name", "last_name", "email", "boards")
        
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

        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            if crypto.validate_passwd(user.salt, password, user.hashed_pwd):
                user.jwt_salt = crypto.create_jwt_id()
                success = True
                user.last_login = timezone.now()
                token = shortcuts.get_token(user, info.context)
                refreshtkn = shortcuts.create_refresh_token(user)
                user.save(update_fields=["last_login", "jwt_salt"])
            else:
                raise GraphQLError("Provided password is incorrect")
        else:
            raise GraphQLError("Provided email is incorrect")

        return LoginUser(user=user, success=success, token=token, refresh_token=refreshtkn)


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        refresh_token = graphene.String(required=True)
        
    def mutate(self, info: ResolveInfo, refresh_token: str):
        jwt_token = info.context.headers['Authorization'].replace('Bearer ','')
        jwt_payload = jwt_utils.decode_token(jwt_token, info.context)
        tkn = shortcuts.get_refresh_token(refresh_token, info.context)
        tkn.revoke()
        user = shortcuts.get_user_by_payload(jwt_payload)
        if(user is None):
            raise exceptions.ObjectDoesNotExist("User doesn't exist for computed payload")
        user.jwt_salt = crypto.create_jwt_id()
        user.save(update_fields=["jwt_salt"])
        
        return LogoutUser(success=True)


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

        if UserModel.objects.filter(email=email).exists():
            raise GraphQLError(f"Given email {email} is in use")
        else:
            user = UserModel(name=name, last_name=last_name, email=email)
            user.set_salt()
            user.set_password(password)
            user.jwt_salt = crypto.create_jwt_id()
            user.save()
            success = True
            token = shortcuts.get_token(user)
            refreshtkn = shortcuts.create_refresh_token(user)
        
        return RegisterUser(user=user, success=success, token=token, refresh_token=refreshtkn)


class Mutation(graphene.ObjectType):
    loginuser = LoginUser.Field()
    registeruser = RegisterUser.Field()
    logoutuser = LogoutUser.Field()