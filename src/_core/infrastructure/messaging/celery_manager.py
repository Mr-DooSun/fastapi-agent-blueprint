# -*- coding: utf-8 -*-
from typing import Any, Dict

from celery import Celery


class CeleryManager:
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def send_task(
        self,
        task_name: str,
        args: tuple = None,
        kwargs: Dict[str, Any] = None,
        **options,
    ):
        return self.celery_app.send_task(task_name, args=args, kwargs=kwargs, **options)
