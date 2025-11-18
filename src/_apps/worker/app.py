from celery import Celery
from kombu.utils.url import safequote

from src._apps.worker.bootstrap import bootstrap_app
from src._apps.worker.di.container import WorkerContainer

container = None


def create_container():
    container = WorkerContainer()

    return container


def create_app():
    global container
    container = create_container()

    env = container.core_container.config.env()
    aws_region = container.core_container.config.sqs.region()
    aws_access_key = safequote(container.core_container.config.sqs.acecss_key())
    aws_secret_key = safequote(container.core_container.config.sqs.secret_key())
    aws_queue = container.core_container.config.sqs.queue()

    app = Celery(broker=f"sqs://{aws_access_key}:{aws_secret_key}@")
    app.conf.broker_transport_options = {
        "region": aws_region,
        "wait_time_seconds": 20,
    }
    app.conf.update(
        result_expires=3600,
        task_ignore_result=True,
    )
    app.conf.task_default_queue = f"{env}-{aws_queue}"

    bootstrap_app(app=app)

    return app


app = create_app()
