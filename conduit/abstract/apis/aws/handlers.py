import concurrent.futures
import logging
import os
import queue
from typing import List, Optional

from botocore.exceptions import ClientError

from .services import AWSClientFactory
from .types import FileMetaData, FileObject

bucket = os.getenv("AWS_BUCKET_NAME")
logger = logging.getLogger("abstract")


class S3AWSHandler:
    def __init__(self) -> None:
        self.client = AWSClientFactory.build_client("s3")
        self.queue = queue.Queue()

    def create_folder(self, path: str) -> None:
        try:
            self.client.put_object(Bucket=bucket, Key=path)
        except Exception as e:
            logger.exception(f"Error creating folder -> {str(e)}")

    def _get_upload_presigned_url(
        self, key: str, metadata: Optional[FileMetaData] = None
    ) -> str:

        try:
            return self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": bucket, "Key": key, "Metadata": metadata},
                ExpiresIn=1000,
            )

        except ClientError:
            logger.info("Couldn't get a presigned URL for object '%s'.", key)

        return ""

    def _get_download_presigned_url(self, path: str) -> str:

        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": path},
                ExpiresIn=1000,
            )
        except ClientError:
            logger.info("Couldn't get a presigned URL for object '%s'.", path)

        return ""

    def get_download_presigned_url(self, path: str) -> str:

        return self._get_download_presigned_url(path)

    def get_upload_presigned_url(
        self,
        file_obj: FileObject,
        root: str = None,
        metadata: Optional[FileMetaData] = None,
    ) -> None:

        full_path = file_obj["path"] if not root else root + file_obj["path"]
        logger.info(f"Processing file : {full_path}")

        metadata["file_path"], metadata["filesize"] = (
            file_obj["path"],
            str(file_obj["filesize"]),
        )
        url = self._get_upload_presigned_url(full_path, metadata)
        file_obj["url"] = url

        self.queue.put(file_obj)

    def fetch_urls(
        self,
        file_objects: List[FileObject],
        root: str = None,
        metadata: Optional[FileMetaData] = None,
    ) -> List[FileObject]:
        files: List[FileObject] = []

        if len(file_objects) > 10:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(32, len(file_objects) // 2)
            ) as exec:
                futures = [
                    exec.submit(self.get_upload_presigned_url, file, root, metadata)
                    for file in file_objects
                ]

                for f in futures:
                    f.result()

            while not self.queue.empty():
                files.append(self.queue.get())

        else:
            for file_obj in file_objects:

                full_path = file_obj["path"] if not root else root + file_obj["path"]
                metadata["file_path"], metadata["filesize"] = (
                    file_obj["path"],
                    str(file_obj["filesize"]),
                )
                file_obj["url"] = self._get_upload_presigned_url(full_path, metadata)
                files.append(file_obj)

        return files
