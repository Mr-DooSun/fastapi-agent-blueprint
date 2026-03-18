from dependency_injector import containers, providers

from src._core.infrastructure.di.core_container import CoreContainer
from src._core.infrastructure.discovery import discover_domains, load_domain_container


def create_server_container() -> containers.DynamicContainer:
    """Server용 DI 컨테이너를 동적으로 생성한다.

    discover_domains()로 탐지된 모든 도메인의 Container를
    자동 등록하므로, 새 도메인 추가 시 이 파일을 수정할 필요 없다.
    """
    container = containers.DynamicContainer()
    container.core_container = providers.Container(CoreContainer)

    for domain in discover_domains():
        domain_container_cls = load_domain_container(domain)
        setattr(
            container,
            f"{domain}_container",
            providers.Container(
                domain_container_cls, core_container=container.core_container
            ),
        )

    return container
