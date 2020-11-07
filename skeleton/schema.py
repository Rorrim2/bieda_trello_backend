import graphene
import skeleton.users.schema
import graphql_jwt
# this file is something like top-level urls.py
# where we define our "endpoints"
        
class Query(skeleton.users.schema.Query, graphene.ObjectType):
    pass

class Mutation(skeleton.users.schema.Mutation, graphene.ObjectType):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)