import os

from abstract.apis.aws.services import AWSClientFactory
from celery import shared_task

from .file_tree import UploadedFile, parse_tree

bucket = os.getenv("AWS_BUCKET_NAME")


@shared_task(name="Handle File Object Upload")
def handle_object_event(key: str):

    s3_client = AWSClientFactory.build_client("s3")
    response = s3_client.head_object(Bucket=bucket, Key=key)
    metadata = response.get("Metadata", {})

    if metadata:
        uploaded_file = UploadedFile(
            author=metadata["owner_email"],
            filepath=metadata["file_path"],
            filesize=metadata["filesize"],
            drive_id=metadata["drive_id"],
        )
        if metadata.get("resource_id"):
            uploaded_file["resource_id"] = metadata["resource_id"]

        parse_tree(uploaded_file)
