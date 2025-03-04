import logging

# import time
from typing import List, Optional

from abstract.apis.aws.types import FileMetaData
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import IntegrityError, transaction
from share.models import Share
from storage.models import Drive, Object

from .utils import delete_connection, setup_db_connection

User: AbstractBaseUser = get_user_model()
logger = logging.getLogger("storage")


class FilePath:
    def __init__(self, metadata: FileMetaData, db_conn_alias: str = "") -> None:

        self.db_conn_alias = setup_db_connection(db_conn_alias)

        self.metadata = metadata

        self.tree: List[Object] = []
        self.parent_path = ""
        self.ids: List[str] = []
        self.ids += metadata["file_path"].split("/")
        self.leaf = self.ids[-1]
        self.file_shared: Optional[Object] = None

        self.drive: Optional[Drive] = None
        self.author: Optional[AbstractBaseUser] = None

    @transaction.atomic
    def parse_path(self):
        try:
            self.drive = (
                Drive.objects.using(self.db_conn_alias)
                .select_for_update()
                .get(pk=self.metadata["drive_id"])
            )
            self.author = User.objects.using(self.db_conn_alias).get(
                uid=self.metadata["author"]
            )

            # set root if a resource exists
            if self.metadata.get("resource_id"):
                parent = (
                    Object.objects.using(self.db_conn_alias)
                    .select_for_update()
                    .get(pk=self.metadata.get("resource_id"), drive=self.drive)
                )
                self.parent_path = parent.path
                self.tree.append(parent)

            for obj in self.ids:

                size = int(self.metadata["filesize"])
                args = {
                    "owner": self.author,
                    "drive": self.drive,
                    "name": obj,
                }
                args["path"] = (
                    f"{self.tree[-1].path}/{obj}"
                    if self.tree
                    else f"{self.parent_path}/{obj}"
                )

                if obj != self.leaf:
                    args["is_directory"] = True

                if Object.objects.using(self.db_conn_alias).filter(**args).exists():
                    file_object = (
                        Object.objects.using(self.db_conn_alias)
                        .prefetch_related("content")
                        .get(**args)
                    )
                    file_object.size += size
                    file_object.save()
                else:
                    args["size"] = size
                    file_object = Object.objects.using(self.db_conn_alias).create(
                        **args
                    )

                if self.ids.index(obj) == 0:
                    self.file_shared = file_object

                if self.tree and file_object not in self.tree[-1].content.all():
                    self.tree[-1].content.add(file_object)

                self.tree.append(file_object)
                print(f"success: ops for {obj}", flush=True)

            transaction.on_commit(self.post_share_ops, using=self.db_conn_alias)

        except (
            IntegrityError,
            Object.DoesNotExist,
            User.DoesNotExist,
            Drive.DoesNotExist,
            Exception,
        ) as e:
            logger.error(f'Error parsing file : {self.metadata["file_path"]}, {str(e)}')
            return []

        if self.db_conn_alias not in ["default", "test_conduit"]:
            delete_connection(self.db_conn_alias)

    def post_share_ops(self):

        args = {
            "pk": self.metadata["share_uid"],
            "drive": self.drive,
            "author": self.author,
            "note": self.metadata["note"],
        }

        if Share.objects.filter(**args).exists():

            share_obj = Share.objects.filter(**args).first()
            share_obj.assets.add(self.file_shared.uid)

        else:
            share_obj = Share.objects.create(**args)  # fix this with single '_'
            share_obj.assets.add(self.file_shared.uid)

        # notification ops here
