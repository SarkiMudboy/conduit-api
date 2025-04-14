import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.test import APIClient
from users.tests.factory import UserFactory
from users.tests.utils import login

from ..choices import DriveType
from ..models import Drive, Object

User: AbstractBaseUser = get_user_model()

ENDPOINTS = {
    "list-drive": "/api/v1/drives/",
    "mod-drive": "/api/v1/drives/",
}


def build_object_endpoint(drive_uid: str, object_uid: str = None) -> str:

    root = ENDPOINTS["mod-drive"] + drive_uid + "/objects/"
    if object_uid:
        return root + object_uid + "/"
    return root


@pytest.mark.django_db
class TestDriveAPI:

    client = APIClient()

    def test_personal_drive_is_created_during_sign_up(self, client):
        user = {
            "email": "test-sample@email.com",
            "tag": "test-sample",
            "password": "testypasswords",
        }

        response = client.post("/api/v1/users/sign-up/", data=user)
        assert response.status_code == 201
        response_data = response.json()

        assert "drive" in response_data.keys()
        assert response_data["drive"]["name"] == "test-sample - drive"
        assert response_data["drive"]["size"] == "5.0GB"

        owner = User.objects.get(email="test-sample@email.com")
        assert Drive.objects.filter(owner=owner, type="personal").exists() is True

    def test_owner_cannot_have_duplicate_personal_drives(self, client):

        user = {
            "email": "test-sample@email.com",
            "tag": "test-sample",
            "password": "testypasswords",
        }

        response = client.post("/api/v1/users/sign-up/", data=user)
        assert response.status_code == 201
        # response_data = response.json()

        owner = User.objects.get(email="test-sample@email.com")
        with pytest.raises(ValueError):
            Drive.objects.create(owner=owner, type="personal")

    def test_unauthorized_user_cannot_view_drives(self, client):

        response = client.get(ENDPOINTS["list-drive"])
        assert response.status_code == 401

    def test_owner_can_list_drives(self, tokens, drive_factory, client):
        conduit_user = tokens["user"]
        token = tokens["tokens"]
        drive_factory.create_batch(4, owner=conduit_user)

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(ENDPOINTS["list-drive"], headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 5

    def test_listed_drive_are_with_correct_data(self, tokens, drive_factory, client):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        test_drive = drive_factory.create(owner=conduit_user)

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(ENDPOINTS["list-drive"], headers=headers)
        assert response.status_code == 200
        response_data = response.json()

        listed_drive = response_data[1]
        personal_drive = conduit_user.user_drive.filter(type=DriveType.PERSONAL).first()
        drive = (
            personal_drive if listed_drive["type"] == DriveType.PERSONAL else test_drive
        )

        assert listed_drive["uid"] == str(drive.uid)
        assert listed_drive["name"] == drive.name
        assert listed_drive["size"] == drive.size
        assert listed_drive["used"] == drive.used
        assert listed_drive["type"] == drive.type

    def test_owner_can_view_drive(self, drive_factory, object_factory, tokens, client):

        conduit_user = tokens["user"]
        token = tokens["tokens"]

        drive = drive_factory.create(
            owner=conduit_user, name=conduit_user.email.split("@")[0]
        )
        objs = object_factory.create_batch(3, drive=drive, owner=conduit_user)
        users = UserFactory.create_batch(5)
        drive.members.add(*[user.uid for user in users])

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            ENDPOINTS["mod-drive"] + str(drive.uid) + "/", headers=headers
        )
        assert response.status_code == 200
        response_data = response.json()

        # check returned data is correct
        assert response_data["uid"] == str(drive.uid)
        assert response_data["name"] == drive.name
        assert response_data["size"] == drive.size
        assert response_data["used"] == drive.used
        assert len(response_data["members"]) == 3

        for member_tag in response_data["members"]:
            assert member_tag in drive.members.values_list("tag", flat=True)

        assert len(response_data["storage_objects"]) == 3

        # check objects are returned correctly
        test_obj = response_data["storage_objects"][0]
        obj = list(filter(lambda o: str(o.uid) == test_obj["uid"], objs))[0]

        assert test_obj["name"] == obj.name
        assert test_obj["size"] == obj.size
        assert test_obj["metadata"] == obj.metadata
        assert test_obj["path"] == obj.path

    def test_owner_can_only_get_active_drives(self, drive_factory, tokens, client):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        drive_factory.create_batch(2, owner=conduit_user, is_active=True)
        drive_factory.create_batch(4, owner=conduit_user, is_active=False)

        headers = {"Authorization": "Bearer " + token["access"]}

        response = client.get(ENDPOINTS["list-drive"], headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 3  # 2 + 1 personal drive

    def test_user_cannot_delete_personal_drive(self, drive_factory, tokens, client):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        personal_drive = conduit_user.user_drive.get(type=DriveType.PERSONAL)
        response = client.delete(
            ENDPOINTS["mod-drive"] + f"{str(personal_drive.uid)}/",
            headers=headers,
        )

        assert response.status_code == 400

    def test_drive_member_can_list_all_associated_drives(
        self, user_factory, drive_factory, client
    ):

        user = user_factory.create()
        member = user_factory.create()
        drive = drive_factory.create(owner=user)
        drive_factory.create_batch(2, owner=member)
        token = login(member)

        drive.members.add(member.uid)
        headers = {"Authorization": "Bearer " + token["access"]}

        response = client.get(ENDPOINTS["list-drive"], headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 4

    def test_drive_member_can_view_accociated_drive(
        self, user_factory, drive_factory, client
    ):

        user = user_factory.create()
        member = user_factory.create()
        drive = drive_factory.create(owner=user)

        token = login(member)

        drive.members.add(member.uid)
        headers = {"Authorization": "Bearer " + token["access"]}

        response = client.get(
            ENDPOINTS["mod-drive"] + f"{str(drive.uid)}/", headers=headers
        )
        assert response.status_code == 200

    def test_drive_member_cannot_delete_drive(
        self, drive_factory, user_factory, client
    ):

        user = user_factory.create()
        member = user_factory.create()
        token = login(member)
        drive = drive_factory.create(owner=user)
        drive.members.add(member.uid)

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.delete(
            ENDPOINTS["mod-drive"] + f"{str(drive.uid)}/", headers=headers
        )

        assert response.status_code == 403

    def test_user_can_delete_drive(self, drive_factory, tokens, client):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        drive = drive_factory.create(owner=conduit_user)
        response = client.delete(
            ENDPOINTS["mod-drive"] + f"{str(drive.uid)}/", headers=headers
        )

        assert response.status_code == 204


@pytest.mark.django_db
class TestObjectAPI:

    client = APIClient()

    def test_owner_can_list_objects_in_drive(
        self, object_factory, drive_factory, tokens, client
    ):

        conduit_user = tokens["user"]
        token = tokens["tokens"]
        drive = drive_factory.create(owner=conduit_user)
        object_factory.create_batch(3, drive=drive)

        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid)), headers=headers
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 3

    def test_drive_member_can_list_objects_in_drive(
        self, object_factory, drive_factory, user_factory, client
    ):

        user = user_factory.create()
        member = user_factory.create()
        token = login(member)

        drive = drive_factory.create(owner=user)
        drive.members.add(member.uid)

        object_factory.create_batch(3, drive=drive)
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid)), headers=headers
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 3

    def test_unauthenticated_user_cannot_access_objects_in_drive(
        self, user_factory, object_factory, client
    ):

        user = user_factory.create()
        object = object_factory.create(drive__owner=user)
        drive = object.drive

        response = client.get(build_object_endpoint(drive_uid=str(drive.uid)))
        assert response.status_code == 401

    def test_unauthorized_user_cannot_access_objects_in_drive(
        self, user_factory, object_factory, tokens, client
    ):

        user = user_factory.create()
        object = object_factory.create(drive__owner=tokens["user"])
        drive = object.drive

        token = login(user)
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid)), headers=headers
        )
        assert response.status_code == 403

    def test_owner_and_drive_member_can_view_object(
        self, user_factory, object_factory, tokens, client
    ):

        user = user_factory.create()
        object = object_factory.create(drive__owner=tokens["user"])
        drive = object.drive
        drive.members.add(user.uid)

        headers = {"Authorization": f"Bearer {tokens['tokens'].get('access')}"}
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid), object_uid=str(object.uid)),
            headers=headers,
        )
        assert response.status_code == 200

        object_data = {
            "uid": str(object.uid),
            "name": object.name,
            "size": object.size,
            "content": [],
            "metadata": {"Author": "Abdul"},
            "path": "/user/",
        }
        response_data = response.json()
        assert response_data == object_data

        token = login(user)
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid), object_uid=str(object.uid)),
            headers=headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == object_data

    def test_only_object_owner_can_delete_object(
        self, user_factory, object_factory, tokens, client
    ):

        user = user_factory.create()
        owner_object = object_factory.create(
            owner=tokens["user"], drive__owner=tokens["user"]
        )

        drive = owner_object.drive
        drive.members.add(user.uid)

        member_object = object_factory.create(owner=user, drive=drive)

        # drive member cannot delete obj
        token = login(user)
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.delete(
            build_object_endpoint(
                drive_uid=str(drive.uid), object_uid=str(owner_object.uid)
            ),
            headers=headers,
        )
        assert response.status_code == 403

        objs = Object.objects.filter(drive=drive)
        assert objs.filter(uid=owner_object.uid).exists() is True
        assert objs.count() == 2

        # owner can..
        headers = {"Authorization": f"Bearer {tokens['tokens'].get('access')}"}
        response = client.delete(
            build_object_endpoint(
                drive_uid=str(drive.uid), object_uid=str(owner_object.uid)
            ),
            headers=headers,
        )
        assert response.status_code == 204

        objs = Object.objects.filter(drive=drive)
        assert objs.filter(uid=owner_object.uid).exists() is False
        assert objs.count() == 1

        # member cannot delete -> Might change later
        token = login(user)
        headers = {"Authorization": f"Bearer {token.get('access')}"}
        response = client.delete(
            build_object_endpoint(
                drive_uid=str(drive.uid), object_uid=str(member_object.uid)
            ),
            headers=headers,
        )

        assert response.status_code == 403

        objs = Object.objects.filter(drive=drive)
        assert objs.filter(uid=member_object.uid).exists() is True
        assert objs.count() == 1

    def test_nested_objects_are_not_listed_in_drive_root(
        self, drive_factory, object_factory, tokens, client
    ):

        drive = drive_factory.create(owner=tokens["user"])
        root_object = object_factory.create(drive=drive)
        nested_objects = object_factory.create_batch(2, drive=drive)
        root_object.content.add(*[obj.uid for obj in nested_objects])

        headers = {"Authorization": f"Bearer {tokens['tokens'].get('access')}"}

        # in /drive/uid (drive detail) route
        response = client.get(
            ENDPOINTS["mod-drive"] + str(drive.uid) + "/",
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data.get("storage_objects")) == 1
        assert response_data["storage_objects"][0]["name"] == root_object.name

        # in /objects route
        response = client.get(
            build_object_endpoint(drive_uid=str(drive.uid)),
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["name"] == root_object.name

    def test_directory_objects_are_returned_correctly(
        self, drive_factory, object_factory, tokens, client
    ):

        drive = drive_factory.create(owner=tokens["user"])
        root_object = object_factory.create(drive=drive)
        nested_objects = object_factory.create_batch(2, drive=drive)
        root_object.content.add(*[obj.uid for obj in nested_objects])

        headers = {"Authorization": f"Bearer {tokens['tokens'].get('access')}"}
        response = client.get(
            build_object_endpoint(
                drive_uid=str(drive.uid), object_uid=str(root_object.uid)
            ),
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()

        assert len(response_data.get("content")) == 2

        content_data = response_data.pop("content")
        assert response_data == {
            "uid": str(root_object.uid),
            "name": root_object.name,
            "size": root_object.size,
            "metadata": {"Author": "Abdul"},
            "path": "/user/",
        }

        nested_content = [
            {
                "uid": str(obj.uid),
                "name": obj.name,
                "size": obj.size,
                "metadata": {"Author": "Abdul"},
                "path": "/user/",
            }
            for obj in nested_objects
        ]
        nested_content.reverse()
        assert content_data == nested_content

    def test_nested_objects_are_returned_correctly(
        self, drive_factory, object_factory, tokens, client
    ):

        drive = drive_factory.create(owner=tokens["user"])
        root_object = object_factory.create(drive=drive)
        nested_object = object_factory.create(drive=drive)
        root_object.content.add(nested_object.uid)

        headers = {"Authorization": f"Bearer {tokens['tokens'].get('access')}"}
        response = client.get(
            build_object_endpoint(
                drive_uid=str(drive.uid), object_uid=str(nested_object.uid)
            ),
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()

        assert response_data == {
            "uid": str(nested_object.uid),
            "name": nested_object.name,
            "size": nested_object.size,
            "content": [],
            "metadata": {"Author": "Abdul"},
            "path": "/user/",
        }
