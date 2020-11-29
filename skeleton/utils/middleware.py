from backend import settings
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from ..models import UserModel
from graphql_jwt import shortcuts
from graphql.type import definition, schema


INTROSPECTION_TYPES = [ 
    "__schema",
    "__directive",
    "__directivelocation",
    "__type",
    "__field",
    "__inputValue",
    "__enumvalue",
    "__typekind",
    "_introspection"
]


class UpdateLastActivityMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserModel.objects.filter(pk=request.user.id).update(last_login=timezone.now())
        response = self.get_response(request)

        return response


class JWTAuthenticationMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user is None:
            request.user = SimpleLazyObject(lambda: get_user(request))
        return self.get_response(request)


class DisableIntrospectionMiddleware(object):

    def resolve(self, next, root, info, **kwargs):
        if info.field_name.lower() in INTROSPECTION_TYPES and settings.DEBUG == False:
            query = definition.GraphQLObjectType(
                "Query", lambda: {"Error": definition.GraphQLField(definition.GraphQLString, resolver=lambda *_: "Invalid query type detected")}
            )
            info.schema = schema.GraphQLSchema(query=query)
            return next(root, info, **kwargs)
        return next(root, info, **kwargs)


class QueryDepthValidationMiddleware(object):
    pass


def get_user(request: HttpRequest):
    try:
        return shortcuts.get_user_by_token(request.headers.get("Authorization", "").replace("Bearer ", ""))
    except Exception as e:
        print(f"get user exc {e}")
        t = request.headers.get("Authorization", "").replace("Bearer ", "")
        print(f"jwt was: {t}")
        return AnonymousUser()

