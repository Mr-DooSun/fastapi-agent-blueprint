from src._core.infrastructure.di.core_container import CoreContainer

# CoreContainer를 통해 Broker 인스턴스 생성 및 관리
container = CoreContainer()
broker = container.broker()
