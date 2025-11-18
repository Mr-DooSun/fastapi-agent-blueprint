from celery import Celery

from src._apps.worker.di.container import WorkerContainer
from src.user.interface.worker.bootstrap.user_bootstrap import bootstrap_user


def bootstrap_app(app: Celery) -> None:
    worker_container = WorkerContainer()

    bootstrap_user(app=app, user_container=worker_container.user_container)
