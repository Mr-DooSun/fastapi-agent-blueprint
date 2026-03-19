# 004. DTO/Entity 책임 재정의

- 상태: Accepted (진화 중)
- 날짜: 2025-07-15
- 관련 이슈: #6, #57
- 관련 PR: #7
- 관련 커밋: `bbfd2bf`, `ceebe9c`

## 배경

프로젝트에서 데이터를 표현하는 객체가 세 종류 있었다:

- **DTO**: 클라이언트와 주고받는 Request/Response 데이터
- **Entity**: 레이어 간 이동 시 데이터를 감싸는 객체
- **Model**: SQLAlchemy ORM 테이블 매핑 객체

이 중 Entity의 역할을 "레이어를 이동할 때 반드시 감싸야 하는 데이터 운반자"로 이해하고,
use case → service → repository 간 이동 시 항상 Entity로 변환하는 구조를 사용했다.

## 문제

### 1. Entity의 역할 오해

DDD에서 Entity는 **비즈니스 행위와 고유 식별자**를 가진 도메인 객체다.
그러나 이 프로젝트에서는 Entity가 비즈니스 로직 없이 순수한 데이터 구조체로만 사용되었다.
이는 사실상 DTO와 동일한 역할이었고, Entity라는 이름만 붙어 있을 뿐이었다.

### 2. 레이어마다 변환 필요

Entity를 필수 경유 객체로 취급하면서, 레이어를 이동할 때마다 변환이 필요해졌다:

```python
# Router에서 Request → Entity 변환
create_data.to_entity(CoreCreateUsersEntity)

# Service 결과 Entity → Response 변환
CoreUsersResponse.from_entity(data)
```

모든 API 핸들러에서 이 변환 코드가 반복되었고,
복수 데이터 처리를 위해 `dto_utils.py`에 `dtos_to_entities()`, `entities_to_dtos()` 유틸리티까지 만들었다.

### 3. 다중상속으로 관심사 혼합

Response DTO가 Entity를 상속하는 구조를 사용했다:

```python
# 문제가 된 다중상속 패턴
class CoreUsersResponse(BaseResponse, CoreUsersEntity):
    pass

class CoreCreateUsersRequest(BaseRequest, CoreCreateUsersEntity):
    pass
```

"응답 형식"(BaseResponse)과 "도메인 데이터"(Entity)라는 서로 다른 관심사를 다중상속으로 섞었다.
이렇게 하면:
- DTO와 Entity의 경계가 모호해짐
- MRO(Method Resolution Order) 충돌 가능성
- Entity 필드 변경이 Response 스키마에 직접 영향

## 결정

### 1단계: to_entity/from_entity 패턴 도입 (커밋 bbfd2bf, 2025-07)

처음에는 변환을 명시적으로 만들어 DTO와 Entity의 책임을 분리하려 했다.

```python
class BaseRequest(ApiConfig):
    def to_entity(self, entity_cls: Type[EntityType]) -> EntityType:
        return entity_cls(**self.model_dump())

class BaseResponse(ApiConfig):
    @classmethod
    def from_entity(cls, entity: Entity) -> ReturnType:
        return cls(**entity.model_dump())
```

### 2단계: Entity 제거, DTO 직접 사용 (이슈 #57, 2026-03)

실제로 사용하면서 매번 Entity로 감싸는 것이 번거롭고,
Entity가 비즈니스 로직 없이 데이터만 들고 있어 존재 이유가 없다는 것을 깨달았다.

리서치를 통해 Entity의 본래 역할을 재학습한 후, 다음과 같이 정리했다:

| 객체 | 역할 | 비즈니스 로직 |
|------|------|-------------|
| DTO | 레이어 간 데이터 전달 | 없음 |
| Entity (DDD) | 도메인 행위 + 식별자 | **있음** |
| Model | DB 테이블 매핑 | 없음 |

이 프로젝트의 도메인 객체에 복잡한 비즈니스 행위가 없으므로,
Entity 레이어를 제거하고 DTO가 레이어 간 데이터 전달을 직접 담당하도록 변경했다.

**현재 규칙:**
- `to_entity()`, `from_entity()` 메서드 사용 금지
- 다중상속 패턴 `class Response(BaseResponse, Entity)` 금지
- Model 객체는 Repository 밖으로 노출 금지
- 변환은 인라인으로: `model_dump()`, `model_validate()`

## 근거

| 기준 | Entity 필수 경유 (이전) | DTO 직접 전달 (현재) |
|------|----------------------|---------------------|
| 변환 보일러플레이트 | 매 핸들러마다 to/from_entity 필요 | 불필요 |
| 관심사 분리 | 다중상속으로 혼합 | DTO와 Model 완전 분리 |
| 코드 복잡도 | dto_utils.py 별도 필요 | 인라인 변환으로 충분 |
| Entity의 가치 | 비즈니스 로직 없이 데이터만 운반 | Entity가 필요한 시점에 도입 |

1. Entity가 비즈니스 행위 없이 데이터만 운반하면 DTO와 중복 — 제거가 합리적
2. 다중상속은 관심사를 혼합하여 변경 영향 범위를 예측하기 어렵게 만듦
3. `model_dump()` / `model_validate()`로 인라인 변환하면 별도 메서드나 유틸리티 불필요

## 교훈

- DDD 개념을 도입할 때, 패턴의 "형식"보다 "목적"을 먼저 이해해야 한다
- Entity는 비즈니스 행위가 있을 때 가치가 있다. CRUD 위주 도메인에서는 DTO로 충분하다
- 확신이 없는 상태로 패턴을 도입하면, 보일러플레이트가 늘어난 뒤에야 문제를 인식하게 된다
- 실제로 코드를 작성하면서 느낀 번거로움이 아키텍처 재검토의 가장 좋은 신호였다
