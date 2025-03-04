import os

from abstract.apis.aws.services import AWSClientFactory
from abstract.apis.aws.types import FileMetaData
from celery import shared_task

from .file_tree import FilePath

bucket = os.getenv("AWS_BUCKET_NAME")


@shared_task(name="Handle File Object Upload")
def handle_object_event(key: str):

    s3_client = AWSClientFactory.build_client("s3")
    response = s3_client.head_object(Bucket=bucket, Key=key)
    metadata = response.get("Metadata", {})
    print(metadata, flush=True)
    if metadata:

        uploaded_file = FileMetaData(**metadata)
        path = FilePath(uploaded_file)
        path.parse_path()
