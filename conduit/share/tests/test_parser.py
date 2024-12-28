import uuid
from typing import Dict

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from storage.models import Object
from storage.tests.factory import DriveFactory, ObjectFactory
from users.tests.factory import UserFactory

from ..file_tree import UploadedFile, parse_tree

"""
test file tree is created properly
test file tree is created in the database properly
test exception during parsing rollsback changes
test parrallel calls to parser is safe
test only one tree height
"""

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
        children = tree_child_nodes
        parsed_children = build(root_obj, {})

        assert parsed_children == children
