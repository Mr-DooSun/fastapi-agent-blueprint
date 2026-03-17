# 000. RabbitMQ에서 Celery로 전환

- 상태: Superseded by [001](001-celery-to-taskiq.md)
- 날짜: 2025-09-10
- 관련 이슈: #16
- 관련 커밋: `1f1db6b`

## 배경

비동기 태스크 처리를 위해 RabbitMQ consumer를 직접 구현하여 사용하고 있었다.
메시지를 발행하고, consumer가 수신하여 처리하는 기본 구조였다.

## 문제

RabbitMQ consumer를 직접 구현하면 관리해야 할 것이 많았다:
- consumer, exchange, queue 설정을 직접 관리
- 커넥션/채널 lifecycle 관리
- 메시지 직렬화/역직렬화 직접 처리
- 재시도, 에러 핸들링 등 boilerplate 코드

비즈니스 로직보다 인프라 코드에 더 많은 시간을 쓰게 되는 구조였다.

## 결정

**Celery + SQS 도입**

## 근거

### 1. FastAPI와 유사한 데코레이터 기반 구조

Celery의 `@task` 데코레이터 + `autodiscover_tasks()` 패턴이 FastAPI의 `@router` + `include_router()` 구조와 유사하다.

```python
# FastAPI — 라우터 등록
@router.post("/user")
async def create_user(...):
    ...

app.include_router(router=user_router.router, prefix="/v1")

# Celery — 태스크 등록
@shared_task(name="{project-name}.user.test")
def consume_task(**kwargs):
    ...

app.autodiscover_tasks(["src.user.interface.consumer.tasks"])
```

기존 프로젝트의 아키텍처 패턴(데코레이터로 핸들러 정의 → bootstrap에서 라우팅 등록)과 일관성을 유지할 수 있었다.

### 2. SQS broker 지원

AWS 인프라를 사용하고 있어서 별도 RabbitMQ 서버를 관리할 필요 없이 SQS를 broker로 활용할 수 있었다. Celery는 kombu를 통해 SQS broker를 안정적으로 지원했다.

### 3. 추상화 수준 향상

consumer 직접 구현 대비 Celery가 제공하는 추상화:
- 메시지 직렬화/역직렬화 자동 처리
- 재시도, timeout 등 설정 기반 관리
- task discovery 자동화

## 후속

Celery 도입 후 API와 Worker 간 비즈니스 로직 공유 가능성을 발견했다.
예를 들어, user id로 사용자 정보를 조회하는 단순 CRUD 로직을 API 핸들러와 Worker task 양쪽에서 사용할 수 있겠다고 판단했다.

그러나 프로젝트의 비즈니스 로직이 모두 `async def`로 작성되어 있어,
Celery의 sync task에서 이를 호출하려면 `asyncio.run()`이 필요했고,
이벤트 루프 충돌 문제가 발생했다.

이 문제는 Celery의 구조적 한계로 판명되어 Taskiq로 전환하게 되었다.
→ [001. Celery에서 Taskiq로 전환](001-celery-to-taskiq.md)
