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

request_password_reset = PasswordView.as_view({"post": "request_password_reset"})

confirm_otp = PasswordView.as_view({"post": "confirm_otp"})

reset_password = PasswordView.as_view({"put": "reset_password"})

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SigninView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    # password recovery
    path(
        "request-reset-password/", request_password_reset, name="request-reset-password"
    ),
    path("confirm-reset-password/", confirm_otp, name="confirm-reset-password"),
    path("reset-password/", reset_password, name="reset-password"),
]

urlpatterns += router.urls
