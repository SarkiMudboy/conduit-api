import os

import boto3


class AWSClientFactory(object):
    @staticmethod
    def build_client(service: str):
        return boto3.client(
            service,
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
