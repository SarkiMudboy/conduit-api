from typing import Any, Tuple, Union
from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from typing import Dict
import pytest
from rest_framework.test import APIClient
from faker import Factory as FakerFactory
from .factory import UserFactory
from django.contrib.auth import get_user_model

User: AbstractBaseUser = get_user_model()
faker = FakerFactory.create()

ENDPOINTS = {
    "sign-up": "/api/v1/users/sign-up/",
    "sign-in": "/api/v1/users/sign-in/",
    "sign-out": "/api/v1/users/sign-out/",
    "refresh": "/api/token/refresh/",
    "users": "/api/v1/users/"
}

@pytest.fixture(scope="function")
def tokens() -> Dict[str, Any]:
    """Helper function for logging in and getting tokens"""
    
    conduit_user = UserFactory.create()
    client = APIClient()
    data = {
        "email": conduit_user.email,
        "password": "its-a-secret" 
    }
    response = client.post(ENDPOINTS["sign-in"], data)
    response_data = response.json()
    
    return {
        "user": conduit_user,
        "tokens": response_data["token"]
    }


@pytest.mark.django_db
class TestUserAuthAPI:

    client = APIClient()

    def test_user_can_sign_up(self, client):

        user = {
            "email": "test-sample@email.com",
            "password": "testypasswords"
        }

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 201
        assert User.objects.filter(email=user["email"]).exists() == True

    def test_user_can_sign_up_with_tag(self, client):
        user = {
            "email": "test-sample@email.com",
            "tag": "testtye345",
            "password": "testypasswords"
        }

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 201

        response_data = response.json()
        assert "tag" in response_data.keys()
        assert response_data.get("tag") == user.get("tag")

        user = User.objects.filter(email=user["email"]).first()
        assert user.tag == response_data.get("tag")

    def test_tag_is_generated_if_not_provided_during_sign_up(self, client):
        user = {
            "email": "test-sample@email.com",
            "password": "testypasswords"
        }

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
            "email": "test-sampleemail.com", # wrong email format
            "tag": "",
            "password": "testypasswords"
        }

        response = client.post(ENDPOINTS["sign-up"], data=user)
        assert response.status_code == 400
        assert User.objects.filter(email=user["email"]).exists() == False

    def test_tags_and_email_are_unique(self, user_factory, client):
        conduit_user = user_factory.create()

        user = {
            "email": conduit_user.email,
            "password": "testypasswords"
        }

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
        response = client.post(ENDPOINTS["sign-out"], data={"refresh": token.get('refresh')})
        assert response.status_code == 204

    def test_refresh_token_blacklisted_upon_sign_out(self, client, tokens):
        token = tokens["tokens"]
        response = client.post(ENDPOINTS["sign-out"], data={"refresh": token.get('refresh')})
        assert response.status_code == 204

        # refresh is invalid
        headers = {
            "Authorization": f"Bearer {token.get('access')}"
        }
        response = client.post(ENDPOINTS["refresh"], headers=headers)
        assert response.status_code == 400



@pytest.mark.django_db
class TestUserAPI:

    client = APIClient()

    def test_user_can_retrieve_details(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        
        headers = {
            "Authorization": f"Bearer {token.get('access')}"
        }
        response = client.get(ENDPOINTS["users"] + f"{conduit_user.uid}/", headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        
        assert response_data['email'] == conduit_user.email
        assert response_data['tag'] == conduit_user.tag
    
    def test_user_can_modify_profile(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        data = {'tag': 'newuser123'}
        headers = {
            "Authorization": f"Bearer {token.get('access')}"
        }
        
        response = client.patch(
            ENDPOINTS["users"] + f"{conduit_user.uid}/", 
            data=data, 
            headers=headers,
            content_type="application/json"
            )

        assert response.status_code == 200
        conduit_user.refresh_from_db()
        response_data = response.json()
        assert response_data['tag'] == 'newuser123'

    def test_user_can_delete_profile(self, client, tokens):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        
        headers = {
            "Authorization": f"Bearer {token.get('access')}"
        }
        response = client.delete(ENDPOINTS["users"] + f"{conduit_user.uid}/", headers=headers)
        assert response.status_code == 204

        assert User.objects.filter(uid=conduit_user.uid).exists() == False