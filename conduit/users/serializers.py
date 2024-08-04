from typing import Dict, Optional

from abstract.utils import parse_querydict
from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, User
from .utils import get_email_token


class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["uid", "email", "password", "tag", "avatar"]
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

    def to_internal_value(self, data):
        data = parse_querydict(data)
        if data.get("tag", None) == "":
            data.pop("tag")
        return super().to_internal_value(data)


class LoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=False, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    tag = serializers.CharField(required=False, write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "tag", "password", "token"]

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


class LogoutSerializer(serializers.ModelSerializer):

    refresh = serializers.CharField(required=True)

    class Meta:
        model = User


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
