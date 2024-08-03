from typing import Dict, Optional, Required
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError

from abstract.utils import parse_querydict
from .models import User
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uid",
            "email",
            "password",
            "tag",
            "avatar"
        ]
        read_only_fields = ["uid"]
        extra_kwargs = {
            "tag": {"required": False},
            "password": {"write_only": True}
        }

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
        fields = [
            "email",
            "tag",
            "password",
            "token"
        ]

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
        return {
            "refresh": str(token),
            "access": str(token.access_token)
        }
    

class LogoutSerializer(serializers.ModelSerializer):
    
    refresh = serializers.CharField(required=True)

    class Meta:
        model = User