import concurrent.futures
import uuid
from functools import partial
from typing import Dict

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from storage.models import Object
from storage.tests.factory import DriveFactory, ObjectFactory
from users.tests.factory import UserFactory

from ..file_tree import UploadedFile, parse_tree

User: AbstractBaseUser = get_user_model()


# a func to create the tree above
def build(root: Object, data: Dict[str, list]) -> Dict[str, list]:

    if not root.content.all():
        return data

    data[root.name] = []
    for child in root.content.all():
        data[root.name].append(child.name)
        data = build(child, data)

    return data


@pytest.mark.django_db
class TestParser:
    def test_file_tree_is_created_properly(
        self, tree_paths, tree_nodes, tree_child_nodes
    ):

        author = UserFactory.create()
        drive = DriveFactory.create(owner=author)
        resource = ObjectFactory.create(
            owner=author, drive=drive, name="root", path="root"
        )
        file = UploadedFile(
            author=author.email,
            file_id=uuid.uuid4(),
            resource_id=resource.pk,
            drive_id=drive.pk,
        )

        for p in tree_paths:

            file["filepath"] = p
            tree = parse_tree(file)
            assert len(tree) != 0

        for n in tree_nodes:
            assert Object.objects.filter(owner=author, drive=drive, name=n).count() == 1

        root_obj = Object.objects.get(name="home")
        parsed_children = build(root_obj, {})

        assert parsed_children == tree_child_nodes

    def test_error_during_parsing_rollsback_changes(self, tree_paths):
        """Test may not be nessecary as the exception is raised when no db action has been taken,
        but I'll leave this here so we can extend it in the future..."""

        author = UserFactory.create()
        drive = DriveFactory.create(owner=author)

        file = UploadedFile(
            author=author.email,
            file_id=uuid.uuid4(),
            resource_id="1234",
            drive_id=drive.pk,
        )

        with pytest.raises(Object.DoesNotExist):
            file["filepath"] = tree_paths[0]
            parse_tree(file)


@pytest.mark.django_db(transaction=True)
class TestParserConcurrency:
    def test_concurrent_calls_to_the_parser_is_safe(self, tree_paths, tree_nodes):
        futures = []
        author = UserFactory.create()
        drive = DriveFactory.create(owner=author, name="vault")
        resource = ObjectFactory.create(
            owner=author, drive=drive, name="root", path="root"
        )
        test_paths = [
            UploadedFile(
                author=author.email,
                file_id=uuid.uuid4(),
                filepath=path,
                resource_id=resource.pk,
                drive_id=drive.pk,
            )
            for path in tree_paths
        ]

        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as process_exec:

            for pos, file_data in enumerate(test_paths):
                uploaded_file = partial(parse_tree, file_data=file_data)
                futures.append(
                    process_exec.submit(uploaded_file(db_conn_alias=f"conn{str(pos)}"))
                )

            for f in futures:
                if not f:
                    continue

        for n in tree_nodes:
            assert Object.objects.filter(owner=author, drive=drive, name=n).count() == 1
