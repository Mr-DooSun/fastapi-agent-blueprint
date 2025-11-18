from celery import Celery

from src.user.infrastructure.di.user_container import UserContainer


def create_user_container(user_container: UserContainer):
    user_container.wire(packages=["src.user.interface.worker.tasks"])
    return user_container


def setup_user_routes(app: Celery):
    app.autodiscover_tasks(["src.user.interface.worker.tasks"])


def bootstrap_user(app: Celery, user_container: UserContainer):
    user_container = create_user_container(user_container=user_container)

    setup_user_routes(app=app)
