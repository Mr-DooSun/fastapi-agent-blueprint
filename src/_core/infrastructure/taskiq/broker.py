from collections.abc import Callable
from typing import TypeVar

from taskiq.abc.result_backend import AsyncResultBackend
from taskiq_aws import SQSBroker

_T = TypeVar("_T")


class CustomSQSBroker(SQSBroker):
    """
    AWS 자격 증명을 수동으로 주입할 수 있는 커스텀 SQSBroker.
    기본 SQSBroker는 환경 변수나 설정 파일에서만 자격 증명을 로드하지만,
    이 클래스는 __init__에서 명시적으로 자격 증명을 받아 설정합니다.
    """

    def __init__(
        self,
        queue_url: str,
        aws_region: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        max_messages: int = 10,
        wait_time: int = 20,
        task_id_generator: Callable[[], str] | None = None,
        result_backend: AsyncResultBackend[_T] | None = None,
    ) -> None:
        super().__init__(
            queue_url=queue_url,
            aws_region=aws_region,
            max_messages=max_messages,
            wait_time=wait_time,
            task_id_generator=task_id_generator,
            result_backend=result_backend,
        )

        if aws_access_key_id and aws_secret_access_key:
            self.session.set_credentials(
                access_key=aws_access_key_id,
                secret_key=aws_secret_access_key,
            )
