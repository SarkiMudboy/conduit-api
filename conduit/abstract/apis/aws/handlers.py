import concurrent.futures
import logging
import os
import queue
from typing import List

from botocore.exceptions import ClientError

from .services import AWSClientFactory
from .types import FileObject

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

    def _get_upload_presigned_url(self, key: str) -> str:

        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=1000,
            )
        except ClientError:
            logger.info("Couldn't get a presigned URL for object '%s'.", key)

        return ""

    def get_upload_presigned_url(self, file_obj: FileObject, root: str = None) -> None:

        full_path = file_obj["path"] if not root else root + file_obj["path"]
        logger.info(f"Processing file : {full_path}")
        url = self._get_upload_presigned_url(full_path)
        file_obj["url"] = url

        self.queue.put(file_obj)

    def fetch_urls(
        self, file_objects: List[FileObject], root: str = None
    ) -> List[FileObject]:
        files: List[FileObject] = []

        if len(file_objects) > 2:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(32, len(file_objects) // 2)
            ) as exec:
                futures = [
                    exec.submit(self.get_upload_presigned_url, file, root)
                    for file in file_objects
                ]

                for f in futures:
                    f.result()

            while not self.queue.empty():
                files.append(self.queue.get())

        else:
            for file_obj in file_objects:
                full_path = file_obj["path"] if not root else root + file_obj["path"]
                file_obj["url"] = self._get_upload_presigned_url(full_path)
                files.append(file_obj)

        # print(files)
        return files
