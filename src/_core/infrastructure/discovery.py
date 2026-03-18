"""도메인 자동 발견 유틸리티.

src/ 하위 도메인 패키지를 자동 탐지하여 DI Container와 Bootstrap에서
수동 등록 없이 도메인을 로딩할 수 있게 한다.

참조: migrations/env_utils.py의 load_models()와 동일한 스캔 패턴 사용.
"""

import importlib
from pathlib import Path


def discover_domains() -> list[str]:
    """src/ 하위 유효 도메인 패키지를 자동 탐지한다.

    유효 도메인 조건:
    - 디렉토리명이 '_' 또는 '.'으로 시작하지 않음
    - __init__.py 존재
    - infrastructure/di/{name}_container.py 존재

    Returns:
        알파벳 순 정렬된 도메인 이름 목록
    """
    src_path = Path(__file__).parent.parent.parent  # src/
    domains = []

    for item in sorted(src_path.iterdir()):
        if item.name.startswith(("_", ".")) or not item.is_dir():
            continue
        if not (item / "__init__.py").exists():
            continue

        container_file = item / "infrastructure" / "di" / f"{item.name}_container.py"
        if container_file.exists():
            domains.append(item.name)

    return domains


def to_class_name(domain_name: str) -> str:
    """snake_case 도메인명을 PascalCase로 변환한다.

    Examples:
        >>> to_class_name("user")
        'User'
        >>> to_class_name("user_profile")
        'UserProfile'
    """
    return "".join(word.capitalize() for word in domain_name.split("_"))


def load_domain_container(domain_name: str):
    """도메인의 DI Container 클래스를 동적으로 로드한다.

    Args:
        domain_name: 도메인 이름 (예: "user")

    Returns:
        Container 클래스 (예: UserContainer)
    """
    module_path = f"src.{domain_name}.infrastructure.di.{domain_name}_container"
    module = importlib.import_module(module_path)
    class_name = f"{to_class_name(domain_name)}Container"
    return getattr(module, class_name)
