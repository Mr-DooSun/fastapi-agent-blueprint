# -*- coding: utf-8 -*-
import io
import os

from minio import Minio


class MinioService:
    def __init__(self, minio_client: Minio, bucket_name: str):
        self.minio_client = minio_client
        self.bucket_name = bucket_name

    def upload_file(self, input_file_path: str, object_name: str) -> None:
        with open(input_file_path, "rb") as file_data:
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=os.path.getsize(input_file_path),
            )

    def upload_stream_file(self, file_stream: io.BytesIO, object_name: str) -> None:
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=file_stream,
            length=file_stream.getbuffer().nbytes,  # 스트림의 크기
        )

    def delete_file(self, object_name: str) -> None:
        self.minio_client.remove_object(self.bucket_name, object_name)
