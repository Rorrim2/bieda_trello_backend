from graphql.error.base import GraphQLError
from graphql_jwt.utils import get_user_by_payload, jwt_payload, jwt_encode, jwt_decode, get_payload
import graphql_jwt.exceptions as exceptions
import jwt
from typing import Dict
from skeleton.models import UserModel
from django.core.handlers.wsgi import WSGIRequest
from graphql_jwt.shortcuts import get_user_by_token
import urllib
import json
from ..utils import crypto
from django.utils import timezone


def get_payload(user: UserModel, context: WSGIRequest=None):
    payload = jwt_payload(user, context)
    if context is not None:
        print("Context is oki doki")
        s = str(context.body, 'utf-8').replace("'",'"')
        print(s)
        document_string = ""
        if s != "":
            document_string = str(json.loads(s)['query'])
        else:
            document_string = str(urllib.parse.unquote(context.META.get("QUERY_STRING", "").split("=")[1]))
        if("refreshToken" in document_string):
            jti = user.jtis.create(value=crypto.create_jwt_id())
            user.jwt_salt = jti.value
            user.last_login = timezone.now()
            user.save(update_fields=["last_login", "jwt_salt"])
    payload["jti"] = user.jwt_salt
    return payload

def get_token(user: UserModel, context=None):
    payload = get_payload(user, context)
    return jwt_encode(payload, context)

def get_user_by_context(context: WSGIRequest):

    if not context.user.is_authenticated:
        raise GraphQLError('User is anonymous')

    token = context.headers['Authorization'].replace('Bearer ','')
    user = get_user_by_token(token, context)
    return user

def decode_token(token: str, context=None):
    payload = {}

    def __verify_payload(payload: Dict):
        user = get_user_by_payload(payload)
        jti = ""
        try:
            jti = payload["jti"]
        except:
            raise jwt.MissingRequiredClaimError("jti")
        if(not user.jtis.filter(value=jti).exists()):
            raise jwt.InvalidTokenError("Token expired by user-logout request")

    try:
        payload = jwt_decode(token, context)
        __verify_payload(payload)        
    except jwt.ExpiredSignature:
        raise exceptions.JSONWebTokenExpired()
    except jwt.DecodeError as e:
        print(e)
        raise exceptions.JSONWebTokenError('Error decoding signature')
    except jwt.InvalidTokenError as j:
        print(j)
        raise exceptions.JSONWebTokenError('Invalid token')
    return payload

