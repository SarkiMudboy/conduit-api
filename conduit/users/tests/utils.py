from typing import Dict

from django.contrib.auth.models import AbstractBaseUser
from rest_framework.test import APIClient


def login(user: AbstractBaseUser) -> Dict[str, str]:

    client = APIClient()
    data = {"email": user.email, "password": "its-a-secret"}
    response = client.post("/api/v1/users/sign-in/", data)
    response_data = response.json()

    return response_data["token"]
