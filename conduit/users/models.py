from django.db import models
from abstract.models import TimestampUUIDMixin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
import random
import string

class User(AbstractBaseUser, PermissionsMixin, TimestampUUIDMixin):
    
    email = models.EmailField(_("Email address"), unique=True)
    tag = models.CharField(_("User's tag"), max_length=300, null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    avatar = models.URLField(_("User's avatar"), default="")

    USERNAME_FIELD = "email"
    objects = UserManager()
    
    def __str__(self) -> str:
        return self.email
    
    def generate_tag(self) -> str:
        email_username = self.email.split("@")[0]
        tag = f"{email_username}{''.join(random.choices(string.ascii_lowercase, k=4))}{random.randint(100, 999)}"
        self.tag = tag
        self.save()

        return tag