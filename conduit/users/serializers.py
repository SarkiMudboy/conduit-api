import random
import string
from typing import Any, Dict, Optional, Tuple, Union

import requests
from abstract.utils import parse_querydict
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.cache import cache
from django.utils import timezone
from oauthlib.oauth2 import WebApplicationClient
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from storage.choices import DriveType
from storage.serializers import UserDriveSerializer

from .models import OTP, User
from .utils import get_email_token


class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()
    drive = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["uid", "email", "password", "tag", "avatar", "drive"]
        read_only_fields = ["uid"]
        extra_kwargs = {"tag": {"required": False}, "password": {"write_only": True}}

    def validate_tag(self, tag: str) -> str:
        if not tag or User.objects.filter(tag=tag).exists():
            raise ValidationError("User with tag already exists")

        return tag

    def create(self, validated_data: Dict[str, str]) -> User:
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def get_avatar(self, user: User) -> Optional[str]:
        return user.avatar or None

    def get_drive(self, user: User) -> Dict[str, Any]:
        drive = user.user_drive.filter(type=DriveType.PERSONAL).first()
        return UserDriveSerializer(drive).data

    def to_internal_value(self, data):
        data = parse_querydict(data)
        if data.get("tag", None) == "":
            data.pop("tag")
        return super().to_internal_value(data)


class BasicUserSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uid", "tag", "avatar"]
        read_only_fields = ["uid", "tag", "avatar"]


class LoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=False, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    tag = serializers.CharField(required=False, write_only=True)
    token = serializers.SerializerMethodField()
    current_user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "tag", "password", "token", "current_user"]

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:

        request = self.context.get("request")
        username = attrs.pop("email") if attrs.get("email") else attrs.pop("tag")
        user = authenticate(request=request, username=username, **attrs)

        if not user:
            raise ValidationError("email/tag or password in not valid")

        attrs["user"] = user
        return attrs

    def get_token(self, data: Dict[str, str]) -> Dict[str, str]:

        user = data.get("user")
        token = RefreshToken.for_user(user)
        return {"refresh": str(token), "access": str(token.access_token)}

    def get_current_user(self, data: Dict[str, str]) -> Dict[str, str]:
        """returns user data here"""

        user = data.get("user")
        return BasicUserSeriailzer(user).data


class LogoutSerializer(serializers.ModelSerializer):

    refresh = serializers.CharField(required=True)

    class Meta:
        model = User


class GitHubCallbackSerializer(serializers.Serializer):

    code = serializers.CharField()
    state = serializers.CharField()

    class Meta:
        fields = ["code", "state"]

    def validate_state(self, state: str) -> str:
        if not cache.get(state):
            raise serializers.ValidationError("Invalid state")

    def get_access_token(
        self, validated_data: Dict[str, Any]
    ) -> Dict[str, Union[list, str]]:

        token_url = "https://github.com/login/oauth/access_token"
        client_id = settings.GITHUB_OAUTH_CLIENT_ID
        client_secret = settings.GITHUB_OAUTH_CLIENT_SECRET

        client = WebApplicationClient(client_id=client_id)

        data = client.prepare_request_body(
            code=validated_data.get("code"),
            redirect_uri=settings.GITHUB_OAUTH_CALLBACK_URL,
            client_id=client_id,
            client_secret=client_secret,
        )

        response = requests.post(token_url, data=data)
        client.parse_request_body_response(response.text)

        return client.token

    def get_user_github_profile(
        self, token: Dict[str, Union[list, str]]
    ) -> Dict[str, str]:

        headers = {"Authorization": "token " + token.get("access_token")}

        response = requests.get("https://api.github.com/user", headers=headers)
        raw = response.json()

        return {
            "email": raw.get("email"),
            "tag": f'{raw["name"]}{"".join(random.choices(string.ascii_lowercase, k=4))}{random.randint(100, 999)}',
            "avatar": raw.get("avatar", ""),
        }

    def authenticate(self, creds: Dict[str, str]) -> Tuple[AbstractBaseUser, bool]:
        """Checks if the user exists or is a new user, authenticates accordingly
        params:
            creds-> A dictionary of email, tag and avatar's url
        return-> user: AbstractBaseUser, created: boolean (True if user was created/False if user exists)
        """
        user: Optional[AbstractBaseUser] = None
        created: bool = False

        if creds.get("email"):
            try:
                user = User.objects.get(email=creds.get("email"))
            except User.DoesNotExist:
                user = User.objects.create(**creds)
                created = True
        else:
            raise ValueError("email is missing")
        return user, created

    def get_token(self, user: AbstractBaseUser) -> Dict[str, str]:
        token = RefreshToken.for_user(user)
        return {"refresh": str(token), "access": str(token.access_token)}

    def save(self) -> AbstractBaseUser:

        client_token = self.get_access_token(self.validated_data)
        credentials = self.get_user_github_profile(client_token)
        user, _ = self.authenticate(creds=credentials)
        return user


class PasswordResetSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "token"]

    def get_token(self, user):
        return get_email_token(user.email)

    def send_password_reset_mail(self) -> None:
        user = self.instance
        user.send_password_reset_mail_with_otp()


class ConfirmOTPSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=300)
    otp = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = OTP
        fields = ["otp", "token"]

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:

        otp_obj = self.instance
        otp_str = attrs.pop("otp")

        if timezone.now() > otp_obj.expiry:
            raise serializers.ValidationError("OTP has expired")
        if otp_str != otp_obj.otp:
            raise serializers.ValidationError("Invalid OTP")

        return attrs

    def update(self, otp, validated_data: Dict[str, str]) -> OTP:
        otp.claimed = True
        otp.save()
        return otp


class ChangePasswordSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=2000, required=True, write_only=True)

    class Meta:
        model = User
        fields = ["password"]

    def validate(self, attrs):
        otp = self.instance.otp
        if not otp.claimed:
            raise serializers.ValidationError("Please confirm your OTP first")

        attrs["otp"] = otp
        return attrs

    def update(self, user, validated_data: Dict[str, str]) -> AbstractBaseUser:
        user.set_password(validated_data.get("password"))
        user.save()
        otp = validated_data.pop("otp", None)
        if otp:
            otp.delete()
        return user


class AppTokenRefreshSerializer(TokenRefreshSerializer):

    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get("refresh_token")
        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise InvalidToken("No valid token found in cookie 'refresh_token'")
