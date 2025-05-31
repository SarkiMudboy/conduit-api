from datetime import timedelta
from typing import Any, Dict, Literal, Optional, TypedDict

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from rest_framework.response import Response


class Token(TypedDict, total=False):
    access: str
    refresh: str


class ResponseParams(TypedDict, total=False):
    status: int
    data: Dict[str, Any]
    token: Token


def set_token_cookie(
    type: Literal["access", "refresh"], value: Any, destroy: bool = False
) -> Dict[str, Any]:

    lifetime = "ACCESS_TOKEN_LIFETIME" if type == "access" else "REFRESH_TOKEN_LIFETIME"
    expiry = timezone.now() + settings.SIMPLE_JWT[lifetime]
    if destroy:
        expiry = timezone.now() + timedelta(hours=-5)

    return {
        "key": (
            settings.SIMPLE_JWT["AUTH_COOKIE"] if type == "access" else "refresh_token"
        ),
        "value": value,
        "expires": expiry,
        "secure": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        "httponly": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        "samesite": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    }


def parse_response(
    params: ResponseParams, response: Optional[HttpResponse] = None
) -> HttpResponse:
    """Custom response with auth tokens cookies injected into View Response"""

    if not response:
        response = Response(status=params.get("status"))

    access_cookie = set_token_cookie("access", params["token"]["access"])
    refresh_cookie = set_token_cookie("refresh", params["token"]["refresh"])

    response.set_cookie(**access_cookie)
    response.set_cookie(**refresh_cookie)
    response.data = params.get("data")
    return response


def parse_redirect_response(tokens: Token, location: str) -> HttpResponseRedirect:

    access_cookie = set_token_cookie("access", tokens.get("access"))
    refresh_cookie = set_token_cookie("refresh", tokens.get("refresh"))

    response = HttpResponseRedirect(location)
    response.set_cookie(**access_cookie)
    response.set_cookie(**refresh_cookie)

    return response


def revoke_session(code: int) -> Response:
    # invalidates access and refresh token cookies
    response = Response(status=code)

    access_cookie = set_token_cookie("access", None, destroy=True)
    refresh_cookie = set_token_cookie("refresh", None, destroy=True)

    response.set_cookie(**access_cookie)
    response.set_cookie(**refresh_cookie)

    return response
