from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpRequest
from typing import Optional
from django.contrib.auth.models import AbstractBaseUser

User = get_user_model()

class EmailTagAuthenticationBackend(object):

    @staticmethod
    def authenticate(request: HttpRequest, username: str =None, password: str=None) -> Optional[AbstractBaseUser]:
        try:
            user = User.objects.get(
                Q(tag=username) | Q(email=username)
            )
        except User.DoesNotExist:
            return None
        
        if user and check_password(password, user.password):
            return user
        
        return None
    
    @staticmethod
    def get_user(user_id: str) -> Optional[AbstractBaseUser]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None