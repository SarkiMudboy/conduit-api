import os
from functools import partial

import boto3
from botocore.config import Config


class AWSClientFactory(object):
    @staticmethod
    def build_client(service: str):
        service_client = partial(
            boto3.client,
            service,
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        if service == "s3":
            return service_client(config=Config(signature_version="s3v4"))
        else:
            return service_client()

        # return boto3.client(
        #     service,
        #     region_name="us-east-1",
        #     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        #     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        # )
