import graphene
import graphql_jwt
from skeleton.users.schema import Query as UserQuery
from skeleton.users.schema import Mutation as UserMutation
from skeleton.boards.schema import Query as BoardQuery
from skeleton.boards.schema import Mutation as BoardMutation
from skeleton.lists.schema import Query as ListQuery
from skeleton.lists.schema import Mutation as ListMutation
from skeleton.cards.schema import Query as CardQuery
from skeleton.cards.schema import Mutation as CardMutation

# this file is something like top-level urls.py
# where we define our "endpoints"


class Query(UserQuery, BoardQuery, ListQuery, CardQuery, graphene.ObjectType):
    pass


class Mutation(UserMutation, graphene.ObjectType):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
