# 001. Celery에서 Taskiq로 전환

- 상태: Accepted
- 날짜: 2025-12-24
- 관련 이슈: #16, #27, #56
- 관련 커밋: `1f1db6b`, `314d09c`, `54d3477`

## 배경

RabbitMQ 직접 구현의 복잡도를 줄이기 위해 Celery + SQS를 도입했다.
(도입 경위: [000. RabbitMQ에서 Celery로 전환](000-rabbitmq-to-celery.md))

Celery 도입 후, API와 Worker 간 비즈니스 로직 공유 가능성을 발견했다.
user id로 사용자 정보를 조회하는 단순 CRUD 로직 등을 API 핸들러와 Worker task 양쪽에서
재사용할 수 있겠다고 판단했다.

그러나 프로젝트의 전체 스택이 async 기반이어서, 비즈니스 로직을 공유하려면
task 함수가 async여야 했고, 이 과정에서 이벤트 루프 충돌 문제가 발생했다.

- SQLAlchemy 2.0 async engine + asyncpg
- aiohttp 기반 HTTP client
- aioboto3 (S3)

Celery 내에서 workaround를 시도하지 않고, async 호환 한계를 인지한 시점에서
바로 async-native 대안을 탐색했다.

## 문제

Celery task는 `sync def`만 지원하므로, async 비즈니스 로직을 호출하려면 `asyncio.run()`이 필요했다.

```python
# Celery 시절 코드 (커밋 314d09c)
@shared_task(name="{project-name}.user.test")
@inject
def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
):
    entity = UserEntity.model_validate(kwargs)
    asyncio.run(user_use_case.process_user(entity=entity))  # 이벤트 루프 충돌
```

### `asyncio.run()` 충돌 원인

이것은 Celery 버전 문제가 아니라 **구조적 한계**다.

**Prefork pool (기본값):**
- `asyncio.run()`은 매 호출마다 새 이벤트 루프를 생성하고 파괴
- SQLAlchemy async session pool, aiohttp client 등은 특정 이벤트 루프에 바인딩됨
- 매번 새 루프 → 커넥션 풀 무효화 → `RuntimeError: Task got Future attached to a different loop`

**Gevent/Eventlet pool:**
- 이미 이벤트 루프가 실행 중인 상태에서 `asyncio.run()` 호출
- `RuntimeError: asyncio.run() cannot be called from a running event loop`

### Celery의 async 지원 현황 (2025-12 기준)
- Celery 5.5.x: `async def` task **미지원**
- GitHub Issue [#6552](https://github.com/celery/celery/issues/6552): 마일스톤 5.7.0 (목표 2026-06)
- 상태: "Design Decision Needed" — 아키텍처 설계 미확정

## 검토한 대안

### 1. 백그라운드 이벤트 루프 패턴
Worker 프로세스당 하나의 persistent 루프를 별도 스레드에서 유지하고, `run_coroutine_threadsafe()`로 호출.

- 커넥션 풀 재활용 가능
- 모든 async 작업이 하나의 스레드에서 실행 → 동시성 병목
- 루프 에러 핸들링, 종료 처리 직접 구현 필요
- DI container의 async provider lifecycle 관리 복잡

### 2. celery-aio-pool
Celery worker pool을 asyncio 기반으로 교체하는 라이브러리.

- 코드 변경 최소, async def task 직접 지원
- 0.1.0rc8 (2024-12) — RC 단계, 프로덕션 리스크
- SQS broker와의 호환성 미검증

### 3. worker_process_init 시그널
Celery 시그널로 worker 프로세스 시작 시 이벤트 루프를 세팅.

- `asyncio.run()`의 "매번 새 루프" 문제 해결
- `run_until_complete()` 중첩 호출 불가
- prefork pool에서 fork 후 루프 상태 불안정

### 4. Taskiq
Python asyncio 네이티브 태스크 큐. task handler가 `async def`로 정의됨.

- async 비즈니스 로직을 await로 직접 호출
- dependency-injector `@inject` + `Provide[]` 패턴이 API와 동일하게 동작
- SQS, Redis, RabbitMQ broker 지원
- 상대적으로 신생 프로젝트, 레퍼런스 적음

## 결정

**Taskiq 채택**

```python
# Taskiq 전환 후 코드 (커밋 54d3477)
@broker.task(task_name="{project-name}.user.test")
@inject
async def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
) -> None:
    entity = UserEntity.model_validate(kwargs)
    await user_use_case.process_user(entity=entity)
```

## 근거

| 기준 | Celery 5.5 | Taskiq |
|------|-----------|--------|
| async 비즈니스 로직 공유 | 불가 (bridge 코드 필요) | 완벽 (await 직접 호출) |
| 이벤트 루프 안정성 | 불안정 | 안정 |
| 운영 생태계 | 강함 (10년+, Flower) | 약함 (신생) |
| DI 통합 | sync/async 경계에서 불안정 | API와 동일 패턴 |
| 코드 중복 | sync 래퍼 필요 | 없음 |

1. 이 프로젝트의 핵심 가치인 "async 비즈니스 로직을 API와 Worker에서 중복 없이 공유"는 Celery로 달성 불가
2. 전체 스택이 async이므로 sync worker와의 호환은 근본적으로 어려움
3. Celery 우회 패턴들은 동작하지만, 인프라 레이어에 숨겨진 복잡도를 추가하여 디버깅을 어렵게 만듦
4. Celery의 운영 안정성 장점은 실재하나, async 호환 workaround의 복잡도가 그 장점을 상쇄

### Celery가 더 나았을 경우
- 비즈니스 로직이 sync인 프로젝트
- Flower 등 모니터링 도구가 필수인 환경
- 대규모 팀에서 Celery 운영 경험이 풍부한 경우
