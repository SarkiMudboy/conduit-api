from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PasswordView,
    SigninView,
    SignOutView,
    SignUpView,
    UserRetrieveUpdateDestroyView,
)

router = DefaultRouter()
router.register("", UserRetrieveUpdateDestroyView, basename="users")

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SigninView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    # password recovery
    path("reset-password/", PasswordView.as_view(), name="request-reset-password"),
]

urlpatterns += router.urls
