from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from ..models import UserModel
from graphql_jwt import shortcuts

class UpdateLastActivityMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserModel.objects.filter(pk=request.user.id).update(last_login=timezone.now())
        response = self.get_response(request)
        # if request.user.is_authenticated:
        #     response['Set-Cookie'] = (f'token={shortcuts.get_token(UserModel.objects.filter(pk=request.user.id))}')
        return response

class JWTAuthenticationMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
        return self.get_response(request)

def get_user(request: HttpRequest):
    try:
        return shortcuts.get_user_by_token(request.headers["Authorization"].replace("Bearer ", ""))
    except Exception as e:
        print(f"get user exc {e}")
        t = request.headers["Authorization"].replace("Bearer ", "")
        print(f"jwt was: {t}")
        return AnonymousUser()

