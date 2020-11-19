from graphene.types.generic import GenericScalar
from graphql_jwt.decorators import csrf_rotation, ensure_token, 
from .jwt_utils import decode_token


class VerifyMixin:
    payload = GenericScalar(required=True)

    @classmethod
    @ensure_token
    def verify(cls, root, info, token, **kwargs):
        return cls(payload=decode_token(token, info.context))