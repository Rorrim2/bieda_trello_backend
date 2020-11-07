from django.utils import timezone
from ..models import UserModel

class UpdateLastActivityMiddleware(object):
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserModel.objects.filter(pk=request.user.id).update(last_login=timezone.now())
        response = self.get_response(request)

        return response