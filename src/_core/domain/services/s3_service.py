# -*- coding: utf-8 -*-

from boto3 import client


class S3Service:
    def __init__(self, s3_client: client, bucket_name: str):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
