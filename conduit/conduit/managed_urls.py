from typing import List

from django.urls import path
from users.views import AppTokenRefreshView, AppTokenVerifyView, set_csrf_token


def add_jwt_urls(urlpatterns: List[str]) -> List[str]:
    urlpatterns += [
        path("api/token/refresh/", AppTokenRefreshView.as_view(), name="token_refresh"),
        path("api/token/verify/", AppTokenVerifyView.as_view(), name="token_verify"),
        path("api/set-csrf-token/", set_csrf_token, name="set-csrf"),
    ]

    return urlpatterns
