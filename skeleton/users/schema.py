import jwt
from skeleton.utils.jwt_utils import get_user_by_context
from graphene_django import DjangoObjectType
import graphene
from graphql.execution.base import ResolveInfo
from graphql_jwt import shortcuts
from django.utils import timezone
from ..utils import crypto, jwt_utils
from .model import UserModel
from django.core import exceptions
from graphql.error import GraphQLError


def _register_password(user: UserModel, password: str) -> dict:
    user.set_salt()
    user.set_password(password)
    user.save()
    return _login(user)

def _login(user: UserModel):
    user.jwt_salt = crypto.create_jwt_id()
    user.last_login = timezone.now()
    user.save(update_fields=["last_login", "jwt_salt"])
    success = True
    token = shortcuts.get_token(user)
    p = shortcuts.get_payload(token)
    payload = {
            "email":p.get("email", ""),
            "exp":p.get("exp", 0), 
            "origIat":p.get("origIat", 0)
        }
    refreshtkn = shortcuts.create_refresh_token(user)

    return {
        "success":success,
        "token":token,
        "refresh_token": refreshtkn,
        "user":user,
        "payload":payload
    }
    

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
    user = graphene.Field(UserType, email=graphene.String(), id=graphene.String())

    def resolve_users(self, info: ResolveInfo, **kwargs):
        return UserModel.objects.all()

    def resolve_user(self, info:ResolveInfo, id:str =None, email:str =None, **kwargs):
        kwargs.update({"id":id} if id is not None else {"email":email})
        return UserModel.objects.all().filter(**kwargs).get()


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()
    payload = graphene.types.generic.GenericScalar()


    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, email: str, password: str):
        user = None

        if not UserModel.objects.filter(email=email).exists():
            raise GraphQLError("Provided email is incorrect")

        user = UserModel.objects.get(email=email)

        if not crypto.validate_passwd(user.salt, password, user.hashed_pwd):
            raise GraphQLError("Provided password is incorrect")
       
        return LoginUser(**_login(user))


class ForgetPasswordRequest(graphene.Mutation):
    forget_token = graphene.String()

    
    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, email: str):
        
        if(info.context.user.is_authenticated):
            raise exceptions.SuspiciousOperation("User is already logged in, it's kinda sus")
        
        if not (UserModel.objects.filter(email=email).exists()):
            raise exceptions.ObjectDoesNotExist('User does not exist')

        user = UserModel.objects.filter(email=email).get()
        user.set_unusable_password()
        user.jwt_salt = crypto.create_jwt_id()
        user.save()
        token = shortcuts.get_token(user, info.context)

        return ForgetPasswordRequest(forget_token=token)


class SetNewPasswordAfterReset(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()
    payload = graphene.types.generic.GenericScalar()


    class Arguments:
        forget_token = graphene.String(required=True)
        new_password = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, forget_token: str, new_password: str):
        
        if(info.context.user.is_authenticated):
            raise exceptions.SuspiciousOperation("User is already logged in, it's kinda sus")

        payload = jwt_utils.decode_token(forget_token, info.context) 
        email = payload["email"]

        if not (UserModel.objects.filter(email=email).exists()):
            raise exceptions.ObjectDoesNotExist('User does not exist')

        user = UserModel.objects.filter(email=email).get()

        if not user.hashed_pwd.startswith(crypto.UNUSABLE_PASSWORD_PREFIX): 
            raise exceptions.SuspiciousOperation("User's password is not marked as unusable, it's kinda sus")
        
        if not (user.jwt_salt == payload["jti"]):
            raise jwt.InvalidTokenError("Token expired by user-logout request")


        return SetNewPasswordAfterReset(**_register_password(user, new_password))


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()


    class Arguments:
        refresh_token = graphene.String(required=True)
        
    def mutate(self, info: ResolveInfo, refresh_token: str):
        user = get_user_by_context(info.context)
        tkn = shortcuts.get_refresh_token(refresh_token, info.context)
        tkn.revoke()

        if(user is None):
            raise exceptions.ObjectDoesNotExist("User doesn't exist for computed payload")
        
        if user.hashed_pwd.startswith(crypto.UNUSABLE_PASSWORD_PREFIX): 
            raise exceptions.SuspiciousOperation("User's password is marked as unusable, it's kinda sus")

        user.jwt_salt = crypto.create_jwt_id()
        user.save(update_fields=["jwt_salt"])
        
        return LogoutUser(success=True)


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()
    payload = graphene.types.generic.GenericScalar()


    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, email: str, password: str, name: str, last_name: str):
        user = None

        if UserModel.objects.filter(email=email).exists():
            raise GraphQLError(f"Given email {email} is in use")
        else:
            user = UserModel(name=name, last_name=last_name, email=email)
        
        return RegisterUser(**_register_password(user, password))


class Mutation(graphene.ObjectType):
    loginuser = LoginUser.Field()
    registeruser = RegisterUser.Field()
    logoutuser = LogoutUser.Field()
    forgetpasswordrequest = ForgetPasswordRequest.Field()
    setnewpasswordaftereset = SetNewPasswordAfterReset.Field()

