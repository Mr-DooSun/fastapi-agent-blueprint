# -*- coding: utf-8 -*-

from celery import Celery
from kombu.utils.url import safequote


def create_celery_app(
    env: str, region: str, access_key: str, secret_key: str, queue: str
) -> Celery:
    app = Celery(broker=f"sqs://{safequote(access_key)}:{safequote(secret_key)}@")
    app.conf.update(
        broker_transport_options={
            "region": region,
            "wait_time_seconds": 20,  # long polling
        },
        task_default_queue=f"{env}-{queue}",
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
    )
    return app
