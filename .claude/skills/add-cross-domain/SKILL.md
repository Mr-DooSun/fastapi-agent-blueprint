---
name: add-cross-domain
argument-hint: "from:consumer to:provider"
description: |
  This skill should be used when the user asks to "도메인 연결",
  "도메인 간 의존성", "cross-domain dependency", "도메인 의존성 추가",
  "다른 도메인 참조", "도메인 간 연결", "Protocol 의존성",
  or needs to wire one domain to depend on another domain's data via Protocol-based DIP.
---

# 도메인 간 의존성 연결

요청: $ARGUMENTS (형식: "from:{consumer} to:{provider}", 예: "from:order to:user")

## 분석

1. consumer(소비자) 도메인과 provider(제공자) 도메인 파악
2. Serena `architecture_conventions` 메모리 읽기 — 객체 역할 및 데이터 흐름 확인
3. consumer가 provider의 어떤 기능을 필요로 하는지 확인
4. 양쪽 도메인의 현재 구조 탐색 (Serena `find_symbol` 사용)

## 핵심 규칙
- consumer의 Service는 provider의 **Protocol**에만 의존 (구현체 직접 import 금지)
- Protocol은 provider의 `domain/protocols/`에 위치 (domain 레이어 간 의존은 허용)
- 실제 구현체 연결은 DI Container에서만 수행
- consumer의 `domain/` 폴더에 provider의 `infrastructure/` import 절대 금지
- DI Container 패턴: **project-dna.md §5** 참조
- Base class import 경로: **project-dna.md §2** 참조

## 구현 순서

### 1. Provider Protocol 확인
`src/{provider}/domain/protocols/{provider}_repository_protocol.py`에서:
- consumer가 필요로 하는 메서드가 이미 있는지 확인
- 없으면 Protocol에 메서드 추가 → Repository에 구현 추가

### 2. Consumer Service 수정
`src/{consumer}/domain/services/{consumer}_service.py`에서:
```python
from src.{provider}.domain.protocols.{provider}_repository_protocol import {Provider}RepositoryProtocol

class {Consumer}Service:
    def __init__(
        self,
        {consumer}_repository: {Consumer}RepositoryProtocol,
        {provider}_repository: {Provider}RepositoryProtocol,  # 추가
    ) -> None:
        self.{consumer}_repository = {consumer}_repository
        self.{provider}_repository = {provider}_repository  # 추가
```

### 3. Consumer DI Container 수정
`src/{consumer}/infrastructure/di/{consumer}_container.py`에서:
```python
from src.{provider}.infrastructure.repositories.{provider}_repository import {Provider}Repository

class {Consumer}Container(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    # Provider repository (외부 도메인)
    {provider}_repository = providers.Singleton(
        {Provider}Repository,
        database=core_container.database,
    )

    {consumer}_repository = providers.Singleton(...)

    {consumer}_service = providers.Factory(
        {Consumer}Service,
        {consumer}_repository={consumer}_repository,
        {provider}_repository={provider}_repository,  # 연결
    )
```

### 4. App DI Container 확인
`src/_apps/server/di/container.py`에서:
- 두 도메인 모두 등록되어 있는지 확인
- 필요시 cross-container 의존성 연결

## 안티패턴 (절대 금지)
- consumer Service에서 provider Service 직접 import (Service 간 의존 금지)
- consumer domain에서 provider infrastructure import
- "공통" 서비스 클래스 생성 — Protocol 의존성으로 해결
- Mapper나 Adapter 클래스 별도 생성

## 검증
1. consumer의 `domain/` 폴더에서 provider `infrastructure` import가 없는지 Grep 확인
2. 양쪽 도메인 테스트 실행:
   ```bash
   pytest tests/unit/{consumer}/ tests/unit/{provider}/ -v
   ```
3. pre-commit 실행
