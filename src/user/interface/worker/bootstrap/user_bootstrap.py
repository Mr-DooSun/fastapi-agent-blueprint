from taskiq import AsyncBroker

from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.worker.tasks import user_test_task


def create_user_container(user_container: UserContainer):
    user_container.wire(modules=[user_test_task])
    return user_container


def bootstrap_user_domain(app: AsyncBroker, user_container: UserContainer):
    create_user_container(user_container=user_container)
