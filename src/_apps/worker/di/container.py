from dependency_injector import containers, providers

from src._core.infrastructure.discovery import discover_domains, load_domain_container


def create_worker_container(core_container) -> containers.DynamicContainer:
    """Worker용 DI 컨테이너를 동적으로 생성한다.

    Args:
        core_container: 외부에서 주입받은 CoreContainer 인스턴스.
            Worker는 broker.py에서 생성한 CoreContainer를 공유한다.
    """
    container = containers.DynamicContainer()
    container.core_container = core_container

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
