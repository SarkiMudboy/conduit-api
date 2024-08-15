import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.test import APIClient
from users.tests.factory import UserFactory
from users.tests.utils import login

from ..choices import DriveType
from ..models import Drive

User: AbstractBaseUser = get_user_model()

ENDPOINTS = {
    "list-drive": "/api/v1/drives/",
    "mod-drive": "/api/v1/drives/",
}


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
            ENDPOINTS["mod-drive"] + f"{str(personal_drive.uid)}/", headers=headers
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
