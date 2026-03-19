# 007. DI 컨테이너 계층화와 Interface별 앱 분리

- 상태: Accepted
- 날짜: 2025-09-09 ~ 2025-11-18
- 관련 이슈: #21, #49
- 관련 PR: #23, #50
- 관련 커밋: `5b96e3b`, `aafdcd4`

## 배경

도메인별 레이어드 아키텍처로 전환한 후([006](006-ddd-layered-architecture.md)),
DI 컨테이너와 애플리케이션 구성에 두 가지 문제가 나타났다.

1. 모든 도메인의 비즈니스 로직과 데이터 로직이 하나의 컨테이너에 집중되어 있었다
2. Server, Worker, Admin이 모두 같은 앱에서 실행되어 인터페이스별 분리가 불가능했다

## 문제

### 1. 단일 컨테이너의 비대화

도메인이 늘어날수록 하나의 컨테이너가 모든 도메인의 Use Case, Service, Repository를 포함하게 되어
컨테이너 자체가 무거워졌다.

### 2. 도메인 간 순환 참조

예를 들어 User 도메인에서 Video 도메인의 기능을 사용하고,
Video 도메인에서도 User 도메인을 참조해야 하는 경우가 있었다.
단일 컨테이너에서는 이 순환 의존성을 해결하기 어려웠다.

### 3. 인터페이스별 요구사항 차이

Server(API), Worker(비동기 태스크), Admin(관리 도구)은 각각:
- 서로 다른 라우터/태스크/뷰가 필요
- 서로 다른 미들웨어 설정이 필요
- 같은 비즈니스 로직(Service, Repository)을 공유

하나의 앱에서 이를 모두 처리하면 불필요한 의존성이 로드된다.

## 결정

### 1단계: 도메인별 컨테이너 + 최상위 ServerContainer (#21, 2025-09)

각 도메인이 자체 DI 컨테이너를 가지고,
이를 조합하는 최상위 컨테이너(`ServerContainer`)를 `_shared/` 폴더에 도입했다.

```python
# src/_shared/infrastructure/di/server_container.py (커밋 5b96e3b)
class ServerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(
        UserContainer, core_container=core_container
    )
```

- 도메인 컨테이너를 분리하여 각 도메인의 의존성을 독립적으로 관리
- 순환 참조는 상위 컨테이너에서 의존성을 주입하여 해결
- 레이어드 아키텍처의 약점인 확장성을 컨테이너 계층으로 보완

### 2단계: _shared → _apps 리팩토링, Interface별 앱 분리 (#49, 2025-11)

`_shared/` 폴더를 `_apps/`로 재구성하여 Server, Worker, Admin을 별도 앱으로 분리했다.

```
# Before (_shared 구조)
src/
├── _shared/infrastructure/di/server_container.py
├── app.py              # 단일 앱
└── celery_app.py       # Celery 앱 (별도)

# After (_apps 구조)
src/
├── _apps/
│   ├── server/         # API 서버
│   │   ├── app.py
│   │   ├── bootstrap.py
│   │   └── di/container.py
│   ├── worker/         # 비동기 태스크 워커
│   │   ├── app.py
│   │   ├── bootstrap.py
│   │   └── di/container.py
│   └── admin/          # 관리 도구
│       ├── app.py
│       ├── bootstrap.py
│       └── di/container.py
└── user/
    └── interface/
        ├── server/     # API 라우터
        └── worker/     # Worker 태스크 (consumer → worker로 개명)
```

각 앱이 독립적인 container와 bootstrap을 가지면서도,
도메인의 Service/Repository 레이어는 공유한다.

## 근거

| 기준 | 단일 컨테이너 + 단일 앱 | 도메인별 컨테이너 + 앱 분리 |
|------|----------------------|--------------------------|
| 컨테이너 크기 | 도메인 증가 시 무한 비대화 | 도메인별 격리, 필요한 것만 로드 |
| 순환 참조 | 해결 어려움 | 상위 컨테이너에서 의존성 주입 |
| 비즈니스 로직 공유 | 해당 없음 (하나의 앱) | Server/Worker/Admin이 같은 Service 재사용 |
| 관리 포인트 | 적음 (1개 앱) | 늘어남 (3개 앱) |
| 독립 배포 | 불가 | 인터페이스별 독립 실행 가능 |

1. **비즈니스 로직 공유가 핵심 이득**: 단순 CRUD 코드와 공통 비즈니스 로직을 Server, Worker, Admin이 함께 사용할 수 있다. 어차피 Worker와 Admin은 별도로 만들어야 하고, 같은 아키텍처에서 관리하면 오히려 관리 포인트가 줄어든다.
2. **컨테이너 계층화**: 레이어드 아키텍처의 약점인 확장성을 DI 컨테이너로 보완한다.
3. **관리 포인트 증가는 감수**: 앱이 3개로 늘어나지만, 공유 가능한 로직의 중복 제거가 더 큰 이득이다.

## 후속

- 이후 Celery가 Taskiq로 전환되면서([001](001-celery-to-taskiq.md)) Worker 앱 구조도 변경됨
- consumer → worker로 네이밍 변경 (커밋 `aafdcd4`에서 함께 진행)
- #57에서 도메인 자동 발견 시스템 도입으로, 새 도메인 추가 시 `_apps/` 내 container 수정이 불필요해짐
