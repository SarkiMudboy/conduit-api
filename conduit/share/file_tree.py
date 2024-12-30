import logging
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
    drive_id: str
    resource_id: Optional[str]


def parse_tree(file_data: UploadedFile, db_conn_alias: str = "default") -> List[Object]:

    setup_db_connection(db_conn_alias)

    tree: List[Object] = []
    try:
        with transaction.atomic(using=db_conn_alias):
            """We are locking the 'drive' row here to allow safe concurrent access and prevent data races"""
            print(
                f'attempting to get lock for {file_data["filepath"]}',
                flush=True,
            )
            drive = (
                Drive.objects.using(db_conn_alias)
                .select_for_update()
                .get(pk=file_data["drive_id"])
            )
            print(
                f'Lock acquired for {file_data["filepath"]}, drive-> {drive.name}',
                flush=True,
            )
            author = User.objects.using(db_conn_alias).get(email=file_data["author"])
            parent_path = ""

            ids: List[str] = []
            ids += file_data["filepath"].split("/")

            # set root if a resource exists

            if file_data.get("resource_id"):
                parent = (
                    Object.objects.using(db_conn_alias)
                    .select_for_update()
                    .get(pk=file_data.get("resource_id"), drive=drive)
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

                if Object.objects.using(db_conn_alias).filter(**args).exists():
                    file_object = (
                        Object.objects.using(db_conn_alias)
                        .prefetch_related("content")
                        .get(**args)
                    )
                else:
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
        print(str(e), flush=True)
        logger.error(f'Error parsing file : {file_data["filepath"]}, {str(e)}')
        return []

    if db_conn_alias != "default":
        delete_connection(db_conn_alias)

    return tree
