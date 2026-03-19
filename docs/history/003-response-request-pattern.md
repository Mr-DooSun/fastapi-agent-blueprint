# 003. Response/Request 패턴 설계

- 상태: Accepted
- 날짜: 2025-03-19 ~ 2025-09-09
- 관련 이슈: #1, #5, #22
- 관련 PR: #2, #24
- 관련 커밋: `cdcbf59`, `42fc118`, `204e325`, `2d4c6fe`, `fd191b3`, `3b69806`, `a05ced4`

## 배경

API 응답 형식은 프론트엔드와의 계약이다.
프로젝트 초기에 조회 API가 단건/다건 모두 존재했고,
다건 조회 시 클라이언트가 오버헤드를 직접 조절할 수 있어야 했다.
프론트엔드에서 페이지네이션 UI를 제공할 수 있으므로, 서버 측에서 페이지네이션 정보를 응답에 포함해야 했다.

또한 에러 발생 시 응답 형식이 통일되지 않아,
의도된 에러와 예상치 못한 에러를 클라이언트가 구분하기 어려웠다.

## 문제

### 1. 페이지네이션 응답 분산 (#1)

초기에 `PaginationResponse`를 별도 클래스로 만들었으나,
이렇게 하면 일반 응답과 페이지네이션 응답이 분리되어 API마다 응답 구조가 달라졌다.

```python
# 초기 구조 (커밋 cdcbf59) — 별도 클래스
class PaginationResponse(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: int
    previous_page: int
```

### 2. Response 포맷 책임 위치 (#1)

response format 로직이 `base_usecase`에 있었는데,
use case는 비즈니스 로직을 담당하는 계층이지 응답 형식을 결정하는 계층이 아니었다.

### 3. Return Type과 response_model 혼재 (#5)

FastAPI의 `response_model` 파라미터와 함수 return type annotation이 혼재하여,
Swagger 문서에 표시되는 응답 스키마와 실제 반환 데이터가 불일치했다.
또한 `data` 필드가 `Any` 타입이어서 타입 안전성이 없었다.

### 4. 에러 응답 비표준화 (#22)

에러 발생 시 응답 형식이 통일되지 않아,
Swagger 문서에 에러 응답 스키마가 표시되지 않았고,
프론트엔드에서 에러 핸들링 로직을 일관되게 작성할 수 없었다.

## 결정

### 1. PaginationInfo를 BaseResponse에 Optional로 통합

페이지네이션이 필요 없는 API도 있으므로 `Optional[PaginationInfo]`로 통합했다.

```python
# 통합 후 (커밋 42fc118)
class PaginationInfo(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: int
    previous_page: int

class BaseResponse(ABC, BaseModel):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[Any] = None
    pagination: Optional[PaginationInfo] = None
```

### 2. Response 포맷 책임을 Controller(Router)로 이동

응답 형식은 인터페이스 관심사이므로 controller(후에 router로 개명)가 담당하도록 변경했다 (커밋 `204e325`).
Use case는 비즈니스 데이터만 반환하고, 이를 응답 형식으로 감싸는 것은 router의 책임이 되었다.

### 3. SuccessResponse와 ErrorResponse 분리

정상 응답에는 `error_code`, `error_details`가 불필요하고,
에러 응답에는 `data`, `pagination`이 불필요하다.
이를 분리하여 각 응답 타입에 필요한 필드만 포함하도록 했다.

```python
# 현재 구조
class SuccessResponse(ApiConfig, Generic[ReturnType]):
    success: bool = True
    message: str = "Request processed successfully"
    data: ReturnType | None = None
    pagination: PaginationInfo | None = None

class ErrorResponse(ApiConfig):
    success: bool = False
    message: str = "Request failed"
    error_code: str | None = None
    error_details: dict | None = None
```

### 4. 글로벌 에러 응답 모델 등록

FastAPI app 설정에 공통 에러 응답(400/401/403/404/500)을 등록하여,
Swagger 문서에 에러 응답 스키마가 자동 표시되도록 했다 (커밋 `a05ced4`).

```python
# src/app.py
app = FastAPI(
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        401: {"model": ErrorResponse, "description": "인증 필요 또는 토큰 불일치"},
        403: {"model": ErrorResponse, "description": "권한 없음"},
        404: {"model": ErrorResponse, "description": "해당 리소스 없음"},
        500: {"model": ErrorResponse, "description": "서버 오류"},
    },
)
```

에러 응답 생성은 ExceptionMiddleware가 담당하여,
의도된 에러(비즈니스 예외)와 가드레일로 잡지 못하는 에러(시스템 예외) 모두를
통합적으로 `ErrorResponse` 형식으로 변환한다.

## 근거

| 결정 | 이유 |
|------|------|
| PaginationInfo Optional 통합 | 단건/다건 조회의 응답 구조 통일. 클라이언트가 pagination 필드 유무로 분기 가능 |
| Response 포맷 → Controller | 응답 형식은 인터페이스 관심사. Use case의 재사용성 보장 (API/Worker 간 공유) |
| Success/Error 응답 분리 | 각 응답에 필요한 필드만 포함하여 의미 명확화. 에러에 data 없고, 성공에 error_code 없음 |
| 글로벌 에러 응답 등록 | Swagger 자동 문서화로 프론트엔드 개발자가 에러 형식을 즉시 확인 가능 |
| data 필드 Generic 타입화 | `Any` → `ReturnType`으로 변경하여 타입 안전성과 Swagger 스키마 정확도 향상 |

## 후속

- `data` 필드의 `Any` → `ReturnType` Generic 타입 변경으로 DTO 타입이 Swagger에 정확히 표시되게 됨
- 이후 DTO/Entity 책임 재정의(→ [004](004-dto-entity-responsibility.md))와 맞물려, 응답 DTO가 도메인 Entity와 분리됨
