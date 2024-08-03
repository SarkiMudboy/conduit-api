from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import SignUpView, SignOutView, SigninView, UserRetrieveUpdateDestroyView


router = DefaultRouter()
router.register("", UserRetrieveUpdateDestroyView, basename="users")

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SigninView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out")
]

urlpatterns += router.urls