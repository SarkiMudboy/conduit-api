import logging

# import time
from typing import List, Optional, TypedDict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import IntegrityError, transaction
from storage.models import Drive, Object

from .utils import delete_connection, setup_db_connection

User: AbstractBaseUser = get_user_model()
logger = logging.getLogger("storage")


class UploadedFile(TypedDict):

    author: str
    file_id: str
    filepath: str
    filesize: int
    drive_id: str
    resource_id: Optional[str]


def parse_tree(file_data: UploadedFile, db_conn_alias: str = "") -> List[Object]:

    db_conn_alias = setup_db_connection(db_conn_alias)
    tree: List[Object] = []
    try:
        with transaction.atomic(using=db_conn_alias):
            """We are locking the 'drive' row here to allow safe concurrent access and prevent data races"""
            drive = (
                Drive.objects.using(db_conn_alias)
                .select_for_update()
                .get(pk=file_data["drive_id"])
            )
            author = User.objects.using(db_conn_alias).get(email=file_data["author"])
            parent_path = ""

            ids: List[str] = []
            ids += file_data["filepath"].split("/")
            leaf = ids[-1]
            print(
                f'Start processing {file_data["filepath"]}, Last file-> {leaf}',
                flush=True,
            )

            # set root if a resource exists
            if file_data.get("resource_id"):
                parent = (
                    Object.objects.using(db_conn_alias)
                    .select_for_update()
                    .get(pk=file_data.get("resource_id"), drive=drive)
                )
                parent_path = parent.path
                tree.append(parent)

            for obj in ids:

                size = int(file_data["filesize"])
                args = {
                    "owner": author,
                    "drive": drive,
                    "name": obj,
                }
                args["path"] = (
                    f"{tree[-1].path}/{obj}" if tree else f"{parent_path}/{obj}"
                )

                if obj != leaf:
                    args["is_directory"] = True

                if Object.objects.using(db_conn_alias).filter(**args).exists():
                    file_object = (
                        Object.objects.using(db_conn_alias)
                        .prefetch_related("content")
                        .get(**args)
                    )
                    file_object.size += size
                    file_object.save()
                else:
                    args["size"] = size
                    file_object = Object.objects.using(db_conn_alias).create(**args)

                if tree and file_object not in tree[-1].content.all():
                    tree[-1].content.add(file_object)

                tree.append(file_object)
                print(f"success: ops for {obj}", flush=True)
    except (
        IntegrityError,
        Object.DoesNotExist,
        User.DoesNotExist,
        Drive.DoesNotExist,
        Exception,
    ) as e:
        logger.error(f'Error parsing file : {file_data["filepath"]}, {str(e)}')
        return []

    if db_conn_alias not in ["default", "test_conduit"]:
        delete_connection(db_conn_alias)

    return tree
