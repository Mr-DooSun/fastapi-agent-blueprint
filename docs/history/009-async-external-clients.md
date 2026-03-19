# 009. 비동기 외부 클라이언트 표준화

- 상태: Accepted
- 날짜: 2025-10-15 ~ 2025-10-21
- 관련 이슈: #37, #43
- 관련 PR: #39, #40, #44
- 관련 커밋: `199f9c2`, `fbf2a3c`, `d70ee0e`

## 배경

프로젝트의 전체 스택이 async 기반이다:
- FastAPI의 라우터 핸들러가 `async def`
- SQLAlchemy 2.0 async engine + asyncpg
- dependency-injector의 async provider

그런데 외부 서비스 호출 시 동기 클라이언트를 사용하고 있었다:
- HTTP 호출: httpx (동기 모드)
- S3 파일 저장: minio (동기 클라이언트)

## 문제

### 동기 클라이언트의 이벤트 루프 블로킹

FastAPI는 `async def` 핸들러를 asyncio 이벤트 루프에서 실행한다.
이 핸들러 내에서 동기 HTTP/S3 호출을 하면, 해당 호출이 완료될 때까지
이벤트 루프가 블로킹되어 다른 요청을 처리할 수 없다.

```
요청 A: [핸들러 시작] ... [동기 HTTP 호출 ← 블로킹] ... [응답]
요청 B:                   [대기 ←────────────────────] ... [핸들러 시작]
```

비동기 클라이언트를 사용하면 I/O 대기 중 이벤트 루프가 다른 요청을 처리할 수 있다:

```
요청 A: [핸들러 시작] ... [await HTTP 호출] ........ [응답]
요청 B:                   [핸들러 시작] ... [await 다른 작업] ... [응답]
```

동시 요청이 늘어날수록 이 차이가 성능 병목으로 나타난다.

## 결정

### 1. aiohttp 기반 HTTP 클라이언트 도입 (#37)

`src/_core/infrastructure/http/http_client.py`에 aiohttp 기반 비동기 HTTP 클라이언트를 구현했다.

외부 API 호출을 추상화하는 Gateway 패턴도 함께 도입했다:
- 기존: `http_repository` — DB 리포지토리와 혼동되는 이름
- 변경: `gateway` — 외부 시스템과의 통신을 담당하는 역할에 맞는 이름

```
src/_core/infrastructure/
├── http/
│   └── http_client.py          # aiohttp 래퍼 (세션 관리, 재시도)
└── gateways/
    └── example_gateway.py      # 외부 API별 게이트웨이
```

### 2. aioboto3 기반 S3 클라이언트 전환 (#43)

minio 동기 클라이언트를 aioboto3 비동기 클라이언트로 교체했다.

```
# Before: minio (동기)
src/_core/domain/services/s3_service.py  # 동기 S3 호출

# After: aioboto3 (비동기)
src/_core/infrastructure/storage/
├── s3_client.py       # aioboto3 세션 관리
└── s3_storage.py      # 비동기 파일 업로드/다운로드/삭제
src/_core/domain/services/file_storage_service.py  # 스토리지 추상화
```

## 검토한 대안 (HTTP 클라이언트)

### httpx (AsyncClient)
- FastAPI 공식 문서에서 테스트용으로 권장
- `httpx.AsyncClient`로 비동기 지원
- 동기/비동기 인터페이스 동일하여 전환 용이
- HTTP/2 지원, requests 호환 인터페이스

### aiohttp
- Python 비동기 HTTP의 사실상 표준 (가장 오래되고 검증된 라이브러리)
- 커넥션 풀 관리가 성숙함
- **순수 async 성능이 httpx보다 우수** — aiohttp는 처음부터 async 전용으로 설계되어 오버헤드가 적음
- WebSocket 클라이언트도 지원

### 선택: aiohttp

| 기준 | httpx | aiohttp |
|------|-------|---------|
| async 성능 | sync/async 겸용 설계로 오버헤드 존재 | async 전용 설계, 더 높은 throughput |
| 커넥션 풀 | 지원 | 더 성숙한 구현 |
| HTTP/2 | 지원 | 미지원 |
| 인터페이스 | requests 호환 | 자체 API |
| 생태계 | FastAPI 테스트에서 주로 사용 | 프로덕션 async HTTP 클라이언트로 가장 널리 사용 |

이 프로젝트는 전체 스택이 async이고, HTTP 클라이언트도 프로덕션 워크로드에서 높은 동시 처리가 필요하다.
httpx는 sync/async 겸용으로 설계되어 async 경로에서도 내부적으로 추가 오버헤드가 있는 반면,
aiohttp는 처음부터 async 전용으로 설계되어 순수 async 성능이 더 높다.
HTTP/2가 당장 필요하지 않은 상황에서 성능이 우선이므로 aiohttp를 선택했다.

## 근거

| 기준 | 동기 클라이언트 (이전) | 비동기 클라이언트 (현재) |
|------|---------------------|----------------------|
| 이벤트 루프 | 블로킹 | 논블로킹 |
| 동시 처리 | I/O 대기 중 다른 요청 처리 불가 | I/O 대기 중 다른 요청 처리 가능 |
| 스택 일관성 | async 핸들러 내 sync 호출 혼재 | 전체 스택 async 통일 |
| S3 도구 | minio (동기, 자체 서버용) | aioboto3 (비동기, AWS 네이티브) |

1. async FastAPI에서 동기 I/O 호출은 이벤트 루프를 블로킹하여 동시 처리 성능을 저하시킨다
2. 전체 스택을 async로 통일하면 이벤트 루프 관련 버그 가능성이 줄어든다
3. minio → aioboto3 전환으로 AWS SQS 등 다른 AWS 서비스와 클라이언트를 통일할 수 있다
