from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

class UserManager(BaseUserManager):

    def create_user(self, email: str, password: str, **extra_fields) -> AbstractBaseUser:
        
        if not email:
            raise ValueError(_("Email must be set"))
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)

        user.save()
        return user
    
    def create_superuser(self, email: str, password: str, **extra_fields) -> AbstractBaseUser:

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff set to True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser set to True"))
        
        return self.create_user(email, password, **extra_fields)