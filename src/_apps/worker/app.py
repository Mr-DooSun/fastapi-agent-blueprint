from taskiq_aws import SQSBroker

from src._apps.worker.bootstrap import bootstrap_app
from src._apps.worker.broker import broker
from src._core.config import settings


def create_app() -> SQSBroker:
    # 환경 변수 로드 및 검증
    if not settings.aws_sqs_access_key:
        raise ValueError("AWS_SQS_ACCESS_KEY is required")
    if not settings.aws_sqs_secret_key:
        raise ValueError("AWS_SQS_SECRET_KEY is required")
    if not settings.aws_sqs_region:
        raise ValueError("AWS_SQS_REGION is required")
    if not settings.aws_sqs_queue:
        raise ValueError("AWS_SQS_QUEUE is required")

    aws_access_key = settings.aws_sqs_access_key
    aws_secret_key = settings.aws_sqs_secret_key
    aws_region = settings.aws_sqs_region
    aws_queue = settings.aws_sqs_queue
    env = settings.env

    # 큐 이름 구성
    queue_name = f"{env}-{aws_queue}"

    # AWS Credential 및 Region 설정
    broker.aws_access_key_id = aws_access_key
    broker.aws_secret_access_key = aws_secret_key
    broker.region_name = aws_region

    # Queue URL 설정
    # 개발 환경(local)인 경우 elasticmq 등을 가정하여 로컬 URL 설정
    if settings.is_dev:
        # ElasticMQ 기본 URL 패턴
        broker.url = f"http://localhost:9324/queue/{queue_name}"
    else:
        # 실제 AWS 환경에서는 큐 이름만으로는 부족할 수 있으나,
        # boto3가 내부적으로 처리하거나 URL 형태여야 함.
        # 여기서는 큐 이름을 그대로 사용
        broker.url = queue_name

    # Bootstrap 실행 (태스크 등록 및 DI 설정)
    bootstrap_app(app=broker)

    return broker


# Taskiq CLI 실행 진입점
app = create_app()
