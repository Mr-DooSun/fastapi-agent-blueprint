# 016. Worker Payload Schema 도입

- Status: Accepted
- Date: 2026-04-06
- Related issue: #37
- Related ADR: [003](003-response-request-pattern.md)(Response/Request Pattern), [004](004-dto-entity-responsibility.md)(DTO/Entity Responsibility)

## Background

프로젝트는 데이터 객체의 역할을 단계적으로 정립해왔다:

- ADR 003에서 Request/Response를 HTTP 통신 계약으로 분리
- ADR 004에서 Entity를 제거하고 DTO를 레이어 간 데이터 운반체로 재정의
- Model은 DB 테이블 매핑 전용으로 Repository 밖 노출 금지

이로써 HTTP 인터페이스(`server/`)에는 `schemas/`를 통해 클라이언트-서버 간 명시적 계약이 존재한다.
그러나 워커 인터페이스(`worker/`)에는 이에 대응하는 계약이 없었다.

워커 태스크는 `**kwargs`로 메시지를 수신하고 도메인 DTO로 직접 검증하는 방식이었다:

```python
async def consume_task(**kwargs):
    dto = UserDTO.model_validate(kwargs)
```

프로젝트 초기에는 도메인이 하나(user)뿐이고 태스크도 단순해서 이 방식이 문제가 되지 않았다.
그러나 10+ 도메인, 5+ 팀원 규모로 확장을 목표하면서,
서로 다른 팀이 Producer(서버)와 Consumer(워커)를 독립적으로 개발할 상황이 예상되었다.
이 시점에서 암묵적 메시지 계약은 실질적 위험이 된다.

## Problem

### 1. 암묵적 계약

Producer가 어떤 필드를 보내야 하는지 코드에서 확인할 수 없다.
`**kwargs`만 보고는 메시지 형태를 알 수 없어, 태스크 내부 로직을 읽어야 한다.

### 2. 도메인 DTO 커플링

도메인 DTO에 필드가 추가/변경되면 기존 메시지가 런타임에 실패한다.
예: `UserDTO`에 `role` 필드가 추가되면, 기존 Producer가 보낸 메시지는
`ValidationError`로 실패하지만 이를 배포 전에 감지할 수 없다.

### 3. Producer 측 검증 불가

메시지를 보내기 전에 형식을 검증할 수단이 없다.
잘못된 형식의 메시지가 큐에 들어가고, Consumer에서 처리 실패 후에야 발견된다.

HTTP 인터페이스는 Request 스키마로 이 세 가지 문제를 이미 해결하고 있었다.
워커 인터페이스에만 같은 수준의 안전장치가 빠져 있는 비대칭이 존재했다.

## Alternatives Considered

### A. schemas/ 디렉토리에 통합

서버 스키마와 같은 디렉토리(`interface/server/schemas/`)에 워커용 스키마도 넣는 방안.

기각 사유: 서버 스키마(camelCase, API용)와 워커 스키마(snake_case, 내부용)의
용도와 설정이 다르며, 이름 충돌과 역할 혼동이 발생한다.

### B. 도메인 DTO 직접 사용 유지

현 상태를 유지하면서 문서로만 계약을 관리하는 방안.

기각 사유: 문서와 코드의 괴리가 필연적으로 발생하며,
컴파일 타임(Pydantic 검증)에 잡을 수 있는 오류를 런타임으로 미루게 된다.

## Decision

`interface/worker/payloads/` 디렉토리에 Payload 스키마를 정의한다.

- **용어**: "Payload" — [AsyncAPI](https://www.asyncapi.com/docs/concepts/asyncapi-document/define-payload) 표준에서 메시지 데이터 스키마를 지칭하는 업계 표준 용어
- **Base 설정**: `frozen=True`(불변 메시지) + `extra="forbid"`(엄격한 계약)
- **위치**: Interface 레이어 (`interface/worker/payloads/`)
- **전달 규칙**: 필드가 같으면 Payload를 Service에 직접 전달 (Router의 Request 직접 전달과 동일 원칙)
- **DTO와 독립**: 필드가 같더라도 별도 선언. 메시지 계약과 도메인 데이터를 독립적으로 진화 가능

```python
# After: 명시적 계약
async def consume_task(**kwargs):
    payload = UserTestPayload.model_validate(kwargs)  # 메시지 계약 검증
    await user_service.process_user(dto=payload)       # 직접 전달 (Router의 Request와 동일 원칙)
```

이로써 프로젝트의 데이터 객체 역할이 4가지로 완성된다:

| 객체 | 역할 | 위치 | 도입 ADR |
|------|------|------|----------|
| Request/Response | HTTP 통신 계약 | `interface/server/schemas/` | 003 |
| Payload | 워커 메시지 계약 | `interface/worker/payloads/` | 016 |
| DTO | 레이어 간 내부 데이터 운반 | `domain/dtos/` | 004 |
| Model | DB 테이블 매핑 | `infrastructure/database/models/` | — |

## Rationale

| 결정 | 근거 |
|------|------|
| 별도 디렉토리(`payloads/`) | 서버 스키마와 역할/설정이 다름. 분리해야 혼동 없음 |
| `frozen=True` | 수신된 메시지는 불변. 태스크 내에서 변경하면 안 됨 |
| `extra="forbid"` | 예상치 못한 필드를 즉시 거부. Producer 실수를 빠르게 감지 |
| DTO와 독립 선언 | 메시지 계약 변경 없이 도메인 DTO 진화 가능 (그 반대도) |
| AsyncAPI "Payload" 용어 | 업계 표준 용어로 팀 간 소통 비용 감소 |
| Payload 직접 전달 | Router의 Request 직접 전달과 동일 원칙. 필드가 같으면 변환 불필요 |
| TaskiqManager 미변경 | Producer는 `payload.model_dump()`로 직렬화. 인프라 레이어에 Application 의존성 추가 불필요 |
