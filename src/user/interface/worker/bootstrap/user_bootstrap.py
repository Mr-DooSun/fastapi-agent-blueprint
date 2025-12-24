from taskiq_aws import SQSBroker

from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.worker.tasks import user_test_task


def create_user_container(user_container: UserContainer):
    user_container.wire(modules=[user_test_task])
    return user_container


def setup_user_routes(app: SQSBroker):
    # Taskiq는 모듈이 임포트될 때 데코레이터를 통해 태스크를 브로커에 등록합니다.
    # 상단에서 user_test_task를 임포트했으므로 별도의 autodiscover가 필요하지 않을 수 있습니다.
    # 하지만 명시적인 등록이 필요한 경우나 패턴 유지를 위해 함수를 남겨둡니다.
    pass


def bootstrap_user(app: SQSBroker, user_container: UserContainer):
    user_container = create_user_container(user_container=user_container)

    setup_user_routes(app=app)
