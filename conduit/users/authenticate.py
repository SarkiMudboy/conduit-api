from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token


def enforce_csrf(request: HttpRequest) -> None:
    """
    Enforce CSRF Validation
    """

    def dummy_get_response(request) -> None:  # pragma: no cover
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    error = check.process_view(request, None, (), {})

    if error:
        raise PermissionDenied(f"CSRF Failed: {error}")


# from -> https://stackoverflow.com/questions/66247988/how-to-store-jwt-tokens-in-httponly-cookies-with-drf-djangorestframework-simplej


class JWTTokenCookieAuthentication(JWTAuthentication):

    raw_token: Optional[str] = None

    def authenticate(self, request: HttpRequest) -> Tuple[AbstractBaseUser, Token]:

        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None

        else:
            raw_token = self.get_raw_token(header)

        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token
