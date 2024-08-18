import logging
import os

import boto3

bucket = os.getenv("AWS_BUCKET_NAME")
logger = logging.getLogger("abstract")


class AWSClientFactory(object):
    @staticmethod
    def build_client(service: str):
        return boto3.client(
            service,
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )


class S3AWSHandler:
    def __init__(self) -> None:
        self.client = AWSClientFactory.build_client("s3")

    def create_folder(self, path: str) -> None:
        try:
            self.client.put_object(Bucket=bucket, Key=path)
        except Exception as e:
            logger.exception(f"Error creating folder -> {str(e)}")
