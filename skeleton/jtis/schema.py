from skeleton.utils import map_id
import graphene
from graphql.execution.base import ResolveInfo
from skeleton.models import UserModel


class RevokeJTI(graphene.Mutation):
    success = graphene.Boolean()


    class Arguments:
        jti = graphene.String(required=True)
        user_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, jti: str, user_id: str):

        user = UserModel.objects.filter(pk=map_id(user_id)).get();
        user.jtis.filter(value=jti).delete()
        user.save()

        return RevokeJTI(success=True)


class Mutation(graphene.ObjectType):
    revokejti = RevokeJTI.Field()