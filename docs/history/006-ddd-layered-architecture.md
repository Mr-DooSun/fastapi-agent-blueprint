# 006. 도메인별 레이어드 아키텍처 전환

- 상태: Accepted
- 날짜: 2025-07-16 ~ 2025-08-24
- 관련 이슈: #19, #10, #9
- 관련 PR: #20, #14, #15
- 관련 커밋: `f59e96b`, `e248abf`, `bad7a62`, `88afd88`, `1567ec3`

## 배경

프로젝트 초기에는 `src/apps/`와 `src/domains/`로 애플리케이션 코드와 도메인 코드를 분리했다.

```
src/
├── apps/
│   ├── monolith/app.py       # 모놀리스 서버
│   ├── gateway/app.py        # API 게이트웨이
│   └── microservices/
│       ├── user/app.py
│       └── chat/app.py
└── domains/
    ├── core/                  # 공통 인프라
    │   ├── application/
    │   ├── domain/
    │   └── infrastructure/
    └── user/
        ├── domain/
        └── server/
```

또한 FastAPI의 라우팅 핸들러를 `controller`로 명명하고 있었다.

## 문제

### 1. 앱/도메인 분리 구조의 관리 복잡성

`apps/`와 `domains/`가 분리되어 있어서, 특정 기능에 문제가 생겼을 때
두 디렉토리를 오가며 코드를 찾아야 했다.
예를 들어 user 도메인의 문제를 추적하려면:
- `src/apps/microservices/user/` — 앱 설정
- `src/domains/user/` — 비즈니스 로직
- `src/domains/core/` — 공통 인프라

세 곳을 확인해야 했다.

### 2. Controller 네이밍 불일치

FastAPI 생태계에서는 라우팅 핸들러를 `Router`로 부른다.
`APIRouter`를 사용하면서 파일명은 `controller`인 것이 혼란을 줬다.

```python
# 불일치: FastAPI의 APIRouter를 사용하면서 controller로 명명
router = APIRouter()  # FastAPI 컨벤션: router
# 파일명: user_controller.py  # 프로젝트 컨벤션: controller
```

### 3. Gateway 앱의 불필요성

API 게이트웨이를 별도 앱(`apps/gateway/`)으로 만들었으나,
단일 서버로 운영하는 현재 구조에서는 사용되지 않는 코드였다.

## 결정

3단계에 걸쳐 구조를 개선했다.

### 1단계: Controller → Router 리네이밍 (#10, 2025-07-16)

FastAPI 컨벤션에 맞춰 `controllers/` 디렉토리를 `routers/`로, 파일명을 `*_router.py`로 변경했다.

### 2단계: WebSocket 라우터 추가 (#9, 2025-07-16)

WebSocket 추가와 함께 라우터를 프로토콜별로 분리했다:

```
routers/
├── api/           # HTTP REST 라우터
│   └── user/
└── websocket/     # WebSocket 라우터
    └── chat/
```

### 3단계: 도메인별 평탄화 (#19, 2025-08-24)

`apps/`와 `domains/`를 제거하고, 각 도메인을 `src/` 바로 아래에 배치했다.

```
# After: 도메인별 평탄화
src/
├── app.py              # 메인 앱 (monolith 흡수)
├── core/               # 공통 인프라
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── user/               # user 도메인 (앱+도메인 통합)
│   ├── domain/
│   ├── infrastructure/
│   └── server/
└── chat/               # chat 도메인
    ├── domain/
    ├── infrastructure/
    └── server/
```

- Gateway 앱 제거 (73줄, 사용되지 않는 코드)
- Monolith 앱을 `src/app.py`로 흡수
- Microservices 앱을 각 도메인 내부로 통합

## 근거

| 기준 | apps/domains 분리 (이전) | 도메인별 평탄화 (현재) |
|------|------------------------|---------------------|
| 코드 탐색 | 3곳(apps, domains, core) 확인 필요 | 도메인 폴더 하나만 열면 됨 |
| 네이밍 | controller (Spring 컨벤션) | router (FastAPI 컨벤션) |
| 불필요 코드 | gateway 앱 존재 | 제거 |
| 도메인 독립성 | 앱 설정과 로직이 분리 | 도메인이 자체 앱 설정 포함 |

1. 도메인 폴더를 최상단에 두면, 문제가 생겼을 때 해당 도메인 폴더를 바로 찾아 열 수 있어 탐색이 빠름
2. FastAPI의 `APIRouter` 네이밍 컨벤션을 따르면 프레임워크 문서와 코드가 일관됨
3. 사용하지 않는 gateway 코드를 제거하여 혼란 방지
4. 87개 파일이 변경된 대규모 리팩토링이었지만, 대부분이 파일 이동이어서 로직 변경은 최소화

## 후속

- 이 구조를 기반으로 DI 컨테이너와 shared 인프라 설계가 진행됨 → [007](007-di-container-and-app-separation.md)
- 이후 도메인 자동 발견 시스템 도입으로, 새 도메인 추가 시 `container.py` 수정이 불필요해짐
