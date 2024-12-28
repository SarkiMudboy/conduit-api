import logging
from typing import List, Optional, TypedDict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import IntegrityError, transaction
from storage.models import Drive, Object

User: AbstractBaseUser = get_user_model()
logger = logging.getLogger("storage")


class UploadedFile(TypedDict):

    author: str
    file_id: str
    filepath: str
    drive_id: str
    resource_id: Optional[str]


def parse_tree(file_data: UploadedFile) -> List[Object]:
    tree: List[Object] = []
    try:
        with transaction.atomic():
            """We are locking the 'drive' row here to prevent race conditions and data corruption"""

            drive = Drive.objects.select_for_update().get(pk=file_data["drive_id"])
            author = User.objects.get(email=file_data["author"])
            parent_path = ""

            ids: List[str] = []
            ids += file_data["filepath"].split("/")

            # set root if a resource exists

            if file_data.get("resource_id"):
                parent = Object.objects.select_for_update().get(
                    pk=file_data.get("resource_id"), drive=drive
                )
                parent_path = parent.path

            for obj in ids:

                args = {
                    "owner": author,
                    "drive": drive,
                    "name": obj,
                }
                args["path"] = (
                    f"{tree[-1].path}/{obj}" if tree else f"{parent_path}/{obj}"
                )

                if Object.objects.filter(**args).exists():
                    file_object = Object.objects.prefetch_related("content").get(**args)
                else:
                    print(f'{obj} dosent exist yet for path -> {args["path"]}')
                    file_object = Object.objects.create(**args)

                if tree and file_object not in tree[-1].content.all():
                    tree[-1].content.add(file_object)

                tree.append(file_object)

    except (
        IntegrityError,
        Object.DoesNotExist,
        User.DoesNotExist,
        Drive.DoesNotExist,
    ) as e:
        print(str(e), flush=True)
        logger.error(f'Error parsing file : {file_data["filepath"]}, {str(e)}')
        return []

    return tree
