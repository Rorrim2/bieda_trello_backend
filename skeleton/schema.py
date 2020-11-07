import graphene
from skeleton.users.schema import Query as UserQuery
from skeleton.users.schema import Mutation as UserMutation
from skeleton.boards.schema import Query as BoardQuery


# this file is something like top-level urls.py
# where we define our "endpoints"

class Query(UserQuery, BoardQuery, graphene.ObjectType):
    pass


class Mutation(UserMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
