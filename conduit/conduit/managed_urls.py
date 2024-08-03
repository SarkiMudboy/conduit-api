from typing import List
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def add_jwt_urls(urlpatterns: List[str]) -> List[str]:
    urlpatterns += [
        path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]

    return urlpatterns