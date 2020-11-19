import graphene
from . import mixins
from graphql_jwt import Refresh

class Verify(mixins.VerifyMixin, graphene.Mutation):

    class Arguments:
        token = graphene.String()

    @classmethod
    def mutate(cls, *args, **kwargs):
        return cls.verify(*args, **kwargs)