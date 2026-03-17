from src._apps.worker.bootstrap import bootstrap_app
from src._apps.worker.broker import broker

# Bootstrap 실행 (태스크 등록 및 DI 설정)
bootstrap_app(app=broker)

# Taskiq CLI 실행 진입점
app = broker
