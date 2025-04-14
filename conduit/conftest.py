from typing import Any, Dict, List, Optional

import pytest
from django.contrib.auth.models import AbstractBaseUser
from pytest_factoryboy import register
from rest_framework.test import APIClient
from storage.models import Object
from storage.tests.factory import DriveFactory, ObjectFactory
from users.tests.factory import OTPFactory, UserFactory

register(UserFactory)
register(OTPFactory)

register(DriveFactory)
register(ObjectFactory)


@pytest.fixture(scope="function")
def tokens(conduit_user: Optional[AbstractBaseUser] = None) -> Dict[str, Any]:
    """Helper function for logging in and getting tokens"""

    if not conduit_user:
        conduit_user = UserFactory.create()

    client = APIClient()
    data = {"email": conduit_user.email, "password": "its-a-secret"}
    response = client.post("/api/v1/users/sign-in/", data)
    response_data = response.json()

    return {"user": conduit_user, "tokens": response_data["token"]}


@pytest.fixture(scope="function")
def tree_paths() -> List[str]:

    return [
        "home/living/entertainment/smart_tv.jpg",
        "home/kitchen/fridge/fruits.json",
        "home/living/table_top/remote.jpg",
        "home/kitchen/cooker/pot.png",
        "home/living/table_top/coffee_book.txt",
    ]


@pytest.fixture(scope="function")
def tree_nodes() -> List[str]:

    return [
        "coffee_book.txt",
        "home",
        "living",
        "table_top",
        "remote.jpg",
        "entertainment",
        "smart_tv.jpg",
        "kitchen",
        "fridge",
        "fruits.json",
        "cooker",
        "pot.png",
    ]


@pytest.fixture(scope="function")
def tree_child_nodes() -> Dict[str, list]:
    return {
        "home": ["living", "kitchen"],
        "living": ["table_top", "entertainment"],
        "kitchen": ["fridge", "cooker"],
        "table_top": ["coffee_book.txt", "remote.jpg"],
        "entertainment": ["smart_tv.jpg"],
        "fridge": ["fruits.json"],
        "cooker": ["pot.png"],
    }


@pytest.fixture(scope="function")
def create_tree(tree_child_nodes: Dict[str, List[str]]) -> Optional[Object]:

    root = None

    conduit_user = UserFactory.create()
    drive = DriveFactory.create(name="test-drive", owner=conduit_user)

    for parent, children in tree_child_nodes.items():
        obj, _ = Object.objects.get_or_create(name=parent, drive=drive)

        if parent == "home":
            obj.path = "/home"
            obj.save()
            root = obj

        for child in children:
            node, _ = Object.objects.get_or_create(
                name=child, drive=drive, path=f"/{obj.path[1:]}/{child}"
            )
            obj.content.add(node)

    return root
