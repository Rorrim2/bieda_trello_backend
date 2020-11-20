from graphql_jwt.utils import get_user_by_payload, jwt_payload, jwt_encode, jwt_decode, get_payload
import graphql_jwt.exceptions as exceptions
import jwt
from typing import Dict
from skeleton.models import UserModel

def get_payload(user: UserModel, context=None):
    payload = jwt_payload(user, context)
    payload["jti"] = user.jwt_salt
    return payload

def get_token(user: UserModel, context=None):
    payload = get_payload(user, context)
    return jwt_encode(payload, context)

def decode_token(token: str, context=None):
    payload = {}
    def __verify_payload(payload: Dict):
        user = get_user_by_payload(payload)
        jti = ""
        try:
            jti = payload["jti"]
        except:
            raise jwt.MissingRequiredClaimError("jti")
        if(user.jwt_salt != jti):
            raise jwt.InvalidTokenError("Token expired by user-logout request")

    try:
        payload = jwt_decode(token, context)
        __verify_payload(payload)        
    except jwt.ExpiredSignature:
        raise exceptions.JSONWebTokenExpired()
    except jwt.DecodeError:
        raise exceptions.JSONWebTokenError('Error decoding signature')
    except jwt.InvalidTokenError as j:
        raise exceptions.JSONWebTokenError('Invalid token\n' + j.message)
    return payload

