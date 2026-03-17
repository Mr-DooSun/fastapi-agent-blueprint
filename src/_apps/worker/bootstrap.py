from taskiq import TaskiqState
from taskiq_aws import SQSBroker

from src._apps.worker.broker import container
from src._apps.worker.di.container import WorkerContainer
from src.user.interface.worker.bootstrap.user_bootstrap import bootstrap_user


def bootstrap_app(app: SQSBroker) -> None:
    @app.on_event("startup")
    async def startup(state: TaskiqState):
        worker_container = WorkerContainer(core_container=container)

        bootstrap_user(app=app, user_container=worker_container.user_container)
