# 008. 배포 환경 분리 및 설정 관리

- 상태: Accepted
- 날짜: 2025-09-15
- 관련 이슈: #26, #38
- 관련 PR: #30
- 관련 커밋: `abe8a6f`, `21fd076`

## 배경

프로젝트가 운영 배포를 준비하면서, 환경별로 다르게 동작해야 하는 설정이 생겼다.
특히 Swagger 문서(docs)와 에러 메시지가 운영 환경에서도 그대로 노출되는 보안 이슈가 있었다.

## 문제

### 1. 운영 환경에서 Swagger 문서 노출

개발 환경과 운영 환경 구분 없이 Swagger UI(`/docs-swagger`)와 ReDoc(`/docs-redoc`)이 항상 노출되었다.
운영 환경에서 API 문서가 공개되면 엔드포인트 구조, 파라미터, 응답 형식 등 내부 정보가 노출된다.

### 2. 에러 메시지 무분별 노출

에러 발생 시 스택 트레이스와 상세 에러 정보가 환경 구분 없이 클라이언트에 반환되어,
운영 환경에서 내부 구현이 노출되는 보안 이슈가 있었다.

### 3. 설정 파일 관리 방식

기존에 `config.yml`로 설정을 관리하고 있었는데,
별도의 YAML 파서가 필요하고 IDE 자동완성이나 타입 검증을 받을 수 없었다.

## 결정

### pydantic-settings 기반 환경 설정 도입

`config.yml`을 제거하고 `pydantic-settings`로 `Settings` 클래스를 만들었다.

```python
# src/_core/config.py (커밋 abe8a6f)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    # 환경별로 docs URL 제어
    # local/dev: Swagger UI 노출
    # prod: None (비노출)
```

### 환경별 API 문서 제어

```python
# src/app.py
settings = Settings()
app = FastAPI(
    docs_url="/docs-swagger" if settings.env != "prod" else None,
    redoc_url="/docs-redoc" if settings.env != "prod" else None,
)
```

### 환경별 에러 메시지 제어

ExceptionMiddleware에서 환경에 따라 에러 트레이스 포함 여부를 결정하도록 변경했다.

## 근거

| 기준 | config.yml | pydantic-settings |
|------|-----------|-------------------|
| 타입 검증 | 없음 (문자열) | 자동 타입 변환/검증 |
| IDE 지원 | 없음 | 자동완성, 타입 힌트 |
| 환경변수 바인딩 | 별도 코드 필요 | 자동 바인딩 |
| 파서 의존성 | PyYAML 필요 | 불필요 (Pydantic 내장) |
| 관리 형태 | `.yml` 파일 | `.py` 파일 (코드와 동일) |

1. **보안이 주요 동기**: 운영 환경에서 docs 노출과 에러 메시지 노출을 환경별로 제어
2. `.py` 파일로 설정을 관리하면 코드와 같은 도구(IDE, 린터, 타입체커)로 관리 가능
3. `pydantic-settings`는 환경변수를 자동으로 바인딩하므로, 12-Factor App 원칙에 부합
