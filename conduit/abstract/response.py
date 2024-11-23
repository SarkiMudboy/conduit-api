from typing import Any, Dict, Literal, TypedDict

from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response


class Token(TypedDict, total=False):
    access: str
    refresh: str


class ResponseParams(TypedDict, total=False):
    status: int
    data: Dict[str, Any]
    token: Token


def set_token_cookie(type: Literal["access", "refresh"], value: Any) -> Dict[str, Any]:

    lifetime = "ACCESS_TOKEN_LIFETIME" if type == "access" else "REFRESH_TOKEN_LIFETIME"
    return {
        "key": settings.SIMPLE_JWT["AUTH_COOKIE"]
        if type == "access"
        else "refresh_token",
        "value": value,
        "expires": settings.SIMPLE_JWT[lifetime],
        "secure": settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        "httponly": settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        "samesite": settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    }


def parse_response(
    params: ResponseParams, response: HttpResponse = Response()
) -> HttpResponse:
    """Custom response with auth tokens cookies injected into View Response"""

    access_cookie = set_token_cookie("access", params["token"]["access"])
    refresh_cookie = set_token_cookie("refresh", params["token"]["refresh"])

    response.set_cookie(**access_cookie)
    response.set_cookie(**refresh_cookie)
    response.data = params.get("data")
    response.status = params.get("status")

    return response
