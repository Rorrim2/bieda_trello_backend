import graphene
import skeleton.users.schema

# this file is something like top-level urls.py
# where we define our "endpoints"
        
class Query(skeleton.users.schema.Query, graphene.ObjectType):
    pass

class Mutation(skeleton.users.schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)