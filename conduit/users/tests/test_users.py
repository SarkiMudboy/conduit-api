from datetime import timedelta
from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from faker import Factory as FakerFactory
from rest_framework.test import APIClient

from ..models import OTP
from ..utils import get_email_token
from .factory import OTPFactory, UserFactory

User: AbstractBaseUser = get_user_model()
faker = FakerFactory.create()

ENDPOINTS = {
    "sign-up": "/api/v1/users/sign-up/",
    "sign-in": "/api/v1/users/sign-in/",
    "sign-out": "/api/v1/users/sign-out/",
    "refresh": "/api/token/refresh/",
    "users": "/api/v1/users/",
    # password recovery
    "request-password-reset": "/api/v1/users/request-reset-password/",
    "confirm": "/api/v1/users/confirm-reset-password/",
    "reset-password": "/api/v1/users/reset-password/",
}


@pytest.fixture(scope="function")
def tokens(conduit_user: Optional[AbstractBaseUser] = None) -> Dict[str, Any]:
    """Helper function for logging in and getting tokens"""

    if not conduit_user:
        conduit_user = UserFactory.create()
    client = APIClient()
    data = {"email": conduit_user.email, "password": "its-a-secret"}
    response = client.post(ENDPOINTS["sign-in"], data)
    response_data = response.json()

    return {"user": conduit_user, "tokens": response_data["token"]}


@pytest.fixture(scope="function")
def otp(conduit_user: Optional[AbstractBaseUser] = None) -> Dict[str, Any]:
    """Fixture to provide otp, email_token and user"""

    password: str = None
    if conduit_user:
        password = OTPFactory.create(owner=conduit_user)
    password = OTPFactory.create()

    email_token = get_email_token(password.owner.email)
    return dict(password=password, email_token=email_token, user=password.owner)


@pytest.mark.django_db
class TestUserAuthAPI:

    client = APIClient()

    def test_user_can_sign_up(self, client):

        user = {"email": "test-sample@email.com", "password": "testypasswords"}

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 201
        assert User.objects.filter(email=user["email"]).exists() is True

    def test_user_can_sign_up_with_tag(self, client):
        user = {
            "email": "test-sample@email.com",
            "tag": "testtye345",
            "password": "testypasswords",
        }

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 201

        response_data = response.json()
        assert "tag" in response_data.keys()
        assert response_data.get("tag") == user.get("tag")

        user = User.objects.filter(email=user["email"]).first()
        assert user.tag == response_data.get("tag")

    def test_tag_is_generated_if_not_provided_during_sign_up(self, client):
        user = {"email": "test-sample@email.com", "password": "testypasswords"}

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 201

        response_data = response.json()
        assert "tag" in response_data.keys()

        # check the tag was generated from email
        email_name = user["email"].split("@")[0]
        assert response_data.get("tag").startswith(email_name)

        user = User.objects.filter(email=user["email"]).first()
        assert user.tag == response_data.get("tag")

    def test_user_cannot_sign_up_with_invalid_details(self, client):
        user = {
            "email": "test-sampleemail.com",  # wrong email format
            "tag": "",
            "password": "testypasswords",
        }

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 400
        assert User.objects.filter(email=user["email"]).exists() is False

    def test_tags_and_email_are_unique(self, user_factory, client):
        conduit_user = user_factory.create()

        user = {"email": conduit_user.email, "password": "testypasswords"}

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 400

        user.pop("email")
        user["tag"] = conduit_user.tag

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 400

    def test_user_can_sign_in(self, user_factory, client):

        conduit_user = user_factory.create()
        user = {
            "email": conduit_user.email,
            "password": "its-a-secret",
        }

        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 200

    def test_user_cannot_sign_in_invalid_credentials(self, user_factory, client):
        conduit_user = user_factory.create()
        invalid_email = faker.email()
        user = {
            "email": invalid_email,
            "password": "its-a-secret",
        }

        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 400

        user["email"] = conduit_user.email
        user["password"] = "secret"

        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 400

    def test_user_can_sign_in_with_tag(self, user_factory, client):
        conduit_user = user_factory.create()
        user = {
            "tag": conduit_user.tag,
            "password": "its-a-secret",
        }
        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 200

    def test_tokens_are_returned_upon_sign_in(self, user_factory, client):

        conduit_user = user_factory.create()
        user = {
            "tag": conduit_user.tag,
            "password": "its-a-secret",
        }
        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 200

        response_data = response.json()
        assert "token" in response_data.keys()
        token = response_data["token"]

        assert "access" in token.keys()
        assert "refresh" in token.keys()

    def test_user_can_sign_out(self, client, tokens):

        token = tokens["tokens"]
        response = client.post(
            ENDPOINTS["sign-out"], data={"refresh": token.get("refresh")}
        )
        assert response.status_code == 204

    def test_refresh_token_blacklisted_upon_sign_out(self, client, tokens):
        token = tokens["tokens"]
        response = client.post(
            ENDPOINTS["sign-out"], data={"refresh": token.get("refresh")}
        )
        assert response.status_code == 204

        # refresh is invalid
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.post(ENDPOINTS["refresh"], headers=headers)
        assert response.status_code == 400


@pytest.mark.django_db
class TestUserAPI:

    client = APIClient()

    def test_user_can_retrieve_details(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            ENDPOINTS["users"] + f"{conduit_user.uid}/", headers=headers
        )
        assert response.status_code == 200

        response_data = response.json()

        assert response_data["email"] == conduit_user.email
        assert response_data["tag"] == conduit_user.tag

    def test_user_can_modify_profile(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        data = {"tag": "newuser123"}
        headers = {"Authorization": f"Bearer {token.get('access')}"}

        response = client.patch(
            ENDPOINTS["users"] + f"{conduit_user.uid}/",
            data=data,
            headers=headers,
            content_type="application/json",
        )

        assert response.status_code == 200
        conduit_user.refresh_from_db()
        response_data = response.json()
        assert response_data["tag"] == "newuser123"

    def test_user_can_delete_profile(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.delete(
            ENDPOINTS["users"] + f"{conduit_user.uid}/", headers=headers
        )
        assert response.status_code == 204

        assert User.objects.filter(uid=conduit_user.uid).exists() is False


@pytest.mark.django_db
class TestPasswordRecoveryAPI:

    client = APIClient()

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_user_can_request_password_reset(
        self, mock_stmp_mail, user_factory, client
    ):
        conduit_user = user_factory.create()
        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_invalid_email_returns_200_regardless(self, user_factory, client):

        user_factory.create()
        data = dict(email="new@exxample.com")
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {}

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_email_token_is_returned_in_response(
        self, mock_stmp_mail, user_factory, client
    ):

        conduit_user = user_factory.create()
        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200

        response_data = response.json()
        assert "token" in response_data.keys()
        assert response_data["token"].startswith(conduit_user.email) is True

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_mail_is_sent_upon_password_reset_request(
        self, mock_stmp_mail, user_factory, client
    ):
        conduit_user = user_factory.create()
        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200
        mock_stmp_mail.assert_called_once()

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_otp_generated_upon_successful_password_request(
        self, mock_stmp_mail, user_factory, client
    ):

        conduit_user = user_factory.create()
        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert OTP.objects.filter(owner=conduit_user).exists() is True

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_correct_otp_is_sent_in_mail(self, mock_stmp_mail, user_factory, client):
        conduit_user = user_factory.create()
        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200
        conduit_user.refresh_from_db()
        password = conduit_user.otp
        assert password.otp in mock_stmp_mail.call_args[0][0][1]

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_incorrect_otp_raises_400(self, mock_stmp_mail, otp, client):

        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": "123456", "token": otp.get("email_token")},
        )

        assert response.status_code == 400

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_nonexistent_otp_raises_404(self, mock_stmp_mail, user_factory, client):

        conduit_user = user_factory.create()
        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": "123456", "token": get_email_token(conduit_user.email)},
        )
        assert response.status_code == 404

    @patch("django.utils.timezone.now")
    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_expired_otp_raises_400(
        self, mock_stmp_mail, mock_timezone_now, otp, client
    ):

        mock_timezone_now.return_value = otp.get("password").expiry + timedelta(hours=3)
        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": otp.get("password").otp, "token": otp.get("email_token")},
        )
        assert response.status_code == 400

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_incorrect_email_token_raises_400(self, mock_stmp_mail, otp, client):

        response = client.post(
            ENDPOINTS["confirm"],
            data={
                "otp": otp.get("password").otp,
                "token": otp.get("email_token") + "uty",
            },
        )

        assert response.status_code == 400

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_correct_otp_returns_correct_token_and_200(
        self, mock_stmp_mail, otp, client
    ):

        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": otp.get("password").otp, "token": otp.get("email_token")},
        )
        assert response.status_code == 200
        response_data = response.json()

        assert "token" in response_data.keys()
        assert response_data["token"] == otp.get("email_token")

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_new_otp_is_created_if_reset_is_requested_again(
        self, mock_stmp_mail, otp, client
    ):

        conduit_user = otp.get("user")
        old_otp = conduit_user.otp.otp

        data = dict(email=conduit_user.email)
        response = client.post(
            ENDPOINTS["request-password-reset"],
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 200
        conduit_user.refresh_from_db()
        password = conduit_user.otp

        assert password.otp != old_otp

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_incorrect_token_during_reset_raises_400(self, mock_stmp_mail, otp, client):

        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": otp.get("password").otp, "token": otp.get("email_token")},
        )
        assert response.status_code == 200

        new_password = "its-not-a-secret"
        response = client.put(
            ENDPOINTS["reset-password"],
            data={"password": new_password, "token": otp.get("email_token") + "uty"},
            content_type="application/json",
        )

        assert response.status_code == 400

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_cannot_reset_password_without_claiming_otp(
        self, mock_stmp_mail, otp, client
    ):

        new_password = "its-not-a-secret"
        response = client.put(
            ENDPOINTS["reset-password"],
            data={"password": new_password, "token": otp.get("email_token")},
            content_type="application/json",
        )

        assert response.status_code == 400

    @patch("abstract.tasks.send_emails.send_smtp_email.delay")
    def test_user_can_reset_password(self, mock_stmp_mail, otp, client):

        response = client.post(
            ENDPOINTS["confirm"],
            data={"otp": otp.get("password").otp, "token": otp.get("email_token")},
        )
        assert response.status_code == 200

        new_password = "its-not-a-secret"
        response = client.put(
            ENDPOINTS["reset-password"],
            data={"password": new_password, "token": otp.get("email_token")},
            content_type="application/json",
        )

        assert response.status_code == 200

        # test new password works
        conduit_user = otp.get("user")
        user = {
            "email": conduit_user.email,
            "password": "its-not-a-secret",
        }
        response = client.post(ENDPOINTS["sign-in"], data=user)
        assert response.status_code == 200
