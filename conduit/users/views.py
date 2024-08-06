from abstract.exceptions import BadRequestException
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse
from rest_framework import generics, viewsets
from rest_framework.exceptions import status
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP
from .serializers import (
    ChangePasswordSerializer,
    ConfirmOTPSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetSerializer,
    UserSerializer,
)
from .utils import retrieve_email_from_token

User = get_user_model()


class SignUpView(generics.GenericAPIView):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRetrieveUpdateDestroyView(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet
):

    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    # def get_object(self):
    #     user_id = self.kwargs.get(self.lookup_field) or None
    #     return get_object_or_404(User, id=user_id)

    def get_object(self) -> AbstractBaseUser:
        return self.request.user

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        user = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.serializer_class(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = self.get_object()
        self.perform_destroy(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance: AbstractBaseUser) -> None:
        instance.delete()


class SigninView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignOutView(generics.GenericAPIView):

    serializer_class = LogoutSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        code = status.HTTP_204_NO_CONTENT
        try:
            refresh = request.data.get("refresh")
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception as e:
            print(str(e))
            code = status.HTTP_400_BAD_REQUEST

        return Response(status=code)


# password recovery
class PasswordView(viewsets.GenericViewSet):

    serializer_class = PasswordResetSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def get_object(self):

        email = None
        token = self.request.data.get("token", None)

        if token:
            email = retrieve_email_from_token(token) if token else None
            if not email:
                raise BadRequestException("Invalid email token")
        else:
            email = self.request.data.get("email", None)

        user = self.queryset.filter(email=email).first()
        if not user:
            raise Http404("User not found")
        return user

    def get_otp(self):
        user = self.get_object()
        try:
            otp = user.otp
        except OTP.DoesNotExist:
            raise Http404("OTP for user does not exist")
        return otp

    def request_password_reset(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_password_reset_mail()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def confirm_otp(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        otp = self.get_otp()
        serializer = ConfirmOTPSerializer(otp, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def reset_password(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = self.get_object()
        serializer = ChangePasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
