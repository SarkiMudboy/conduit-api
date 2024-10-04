from typing import List

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


def add_jwt_urls(urlpatterns: List[str]) -> List[str]:
    urlpatterns += [
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    ]

    return urlpatterns
