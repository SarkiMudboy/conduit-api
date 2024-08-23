import random
import secrets
import string

from abstract.models import TimestampUUIDMixin
from abstract.services.email.clients import EmailClient
from abstract.services.email.types import EmailData
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from storage.choices import DriveType
from storage.models import Drive

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimestampUUIDMixin):

    email = models.EmailField(_("Email address"), unique=True)
    tag = models.CharField(
        _("User's tag"), max_length=300, null=True, blank=True, unique=True
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    avatar = models.URLField(_("User's avatar"), default="")

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def generate_tag(self) -> str:
        email_username = self.username
        tag = f"{email_username}{''.join(random.choices(string.ascii_lowercase, k=4))}{random.randint(100, 999)}"
        self.tag = tag
        self.save()

        return tag

    @property
    def username(self) -> str:
        return self.email.split("@")[0]

    def send_password_reset_mail_with_otp(self):

        try:
            otp = self.otp
            otp.delete()
        except OTP.DoesNotExist:
            pass

        token = OTP.objects.create(
            owner=self, expiry=timezone.now() + timezone.timedelta(minutes=10)
        )
        token.generate_otp()

        email_data: EmailData = {
            "subject": "Password Reset",
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "to_email": [self.email],
            "template": "emails/passwords/password_reset_mail.html",
            "context": {"otp": token.otp},
        }

        EmailClient.send(email_data)

    def prep_personal_drive(self):

        Drive.objects.create(
            owner=self,
            name=self.tag + " - drive",
            type=DriveType.PERSONAL,
            size=5000000.0,
            used=0.0,
        )


class OTP(TimestampUUIDMixin):

    owner = models.OneToOneField(User, related_name="otp", on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True, null=True)
    expiry = models.DateTimeField()
    claimed = models.BooleanField(default=False)

    def generate_otp(self) -> None:
        """Generate a random 6 digit OTP"""
        self.otp = "".join(f"{secrets.randbelow(10)}" for _ in range(6))
        self.save()

    def __str__(self) -> str:
        return self.owner.email + " - " + self.otp
