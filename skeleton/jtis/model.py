from django.db import models
from ..utils.crypto import create_jwt_id
from skeleton.users.model import UserModel

class JTIModel(models.Model):
    value = models.CharField(max_length=128, default=create_jwt_id)
    user = models.ForeignKey(to=UserModel, on_delete=models.CASCADE, related_name="jtis")
