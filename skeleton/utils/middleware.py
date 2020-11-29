from graphql.error.base import GraphQLError
from graphql.execution.base import ResolveInfo
from graphql.backend.core import GraphQLCoreBackend
from six import raise_from
from backend import settings
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from ..models import UserModel
from graphql_jwt import shortcuts
from graphql.type import definition, schema, scalars
from typing import List, Dict
import json
from graphql.language.ast import (
    Document,
    FragmentDefinition,
    OperationDefinition,
    Node,
    FragmentSpread,
    Field,
    InlineFragment,
)

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

    def resolve(self, next, root, info: ResolveInfo, **kwargs):

        if info.field_name.lower() in INTROSPECTION_TYPES and settings.DEBUG == False:
            query = definition.GraphQLObjectType(
                "Query", lambda: {"Error": definition.GraphQLField(scalars.GraphQLString, resolver=lambda *_: "Invalid query type detected")}
            )
            info.schema = schema.GraphQLSchema(query=query)
            return next(root, info, **kwargs)
        return next(root, info, **kwargs)


class QueryDepthValidationMiddleware(object):

     def resolve(self, next, root, info: ResolveInfo, **kwargs):
        if settings.DEBUG == False:
            s = str(info.context.body, 'utf-8').replace("'",'"')
            document_string = json.loads(s)['query']
            gql_backend = GraphQLCoreBackend()
            document = gql_backend.document_from_string(info.schema, document_string)
            validate_depth(document.document_ast)

        return next(root, info, **kwargs)


def get_fragments(definitions) -> Dict[str, FragmentDefinition]:
    return {
        definition.name.value: definition
        for definition in definitions
        if isinstance(definition, FragmentDefinition)
    }


def get_queries_and_mutations(definitions) -> List[OperationDefinition]:
    return [
        definition
        for definition in definitions
        if isinstance(definition, OperationDefinition)
    ]


def measure_depth(node:Node, fragments: Dict[str, FragmentDefinition]):
    if isinstance(node, FragmentSpread):
        fragment = fragments.get(node.name.value)
        return measure_depth(node=fragment, fragments=fragments)

    elif isinstance(node, Field):
        if not node.selection_set:
            return 1

        depths = []
        for selection in node.selection_set.selections:
            depth = measure_depth(node=selection, fragments=fragments)
            depths.append(depth)

            if 1 + depth > settings.MAX_QUERY_DEPTH:
                raise GraphQLError("Query depth exceeded. Aborting")

        return 1 + max(depths)

    elif (
        isinstance(node, FragmentDefinition)
        or isinstance(node, OperationDefinition)
        or isinstance(node, InlineFragment)
    ):
        depths = []
        for selection in node.selection_set.selections:
            depth = measure_depth(node=selection, fragments=fragments)
            depths.append(depth)

            if depth > settings.MAX_QUERY_DEPTH:
                raise GraphQLError("Query depth exceeded. Aborting")

        return max(depths)
    else:
        print(type(node))
        raise Exception("Unknown node")


def validate_depth(document: Document):
    
    fragments = get_fragments(document.definitions)
    queries = get_queries_and_mutations(document.definitions)

    for query in queries:
        depth = measure_depth(query, fragments)
        if depth > settings.MAX_QUERY_DEPTH:
            raise GraphQLError("Query depth exceeded. Aborting")


def get_user(request: HttpRequest):
    try:
        return shortcuts.get_user_by_token(request.headers.get("Authorization", "").replace("Bearer ", ""))
    except Exception as e:
        print(f"get user exc {e}")
        t = request.headers.get("Authorization", "").replace("Bearer ", "")
        print(f"jwt was: {t}")
        return AnonymousUser()

