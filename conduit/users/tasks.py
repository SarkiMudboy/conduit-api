from abstract.apis.aws.handlers import S3AWSHandler
from celery import shared_task


@shared_task(name="Create dedicated S3 dir folder for user")
def create_block_folder(path: str) -> None:

    handler = S3AWSHandler()
    handler.create_folder(path)
