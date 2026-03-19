# Architecture Decision History

이 프로젝트의 기술 스택 선택 근거를 기록합니다.
각 문서는 "왜 이 기술을 선택했는가"에 대한 맥락과 판단 기준을 담고 있습니다.

## 목차

| # | 제목 | 상태 | 작성 | 날짜 |
|---|------|------|------|------|
| [000](000-rabbitmq-to-celery.md) | RabbitMQ에서 Celery로 전환 | Superseded by 001 | Done | 2025-09-10 |
| [001](001-celery-to-taskiq.md) | Celery에서 Taskiq로 전환 | Accepted | Done | 2025-12-24 |
| [002](002-serena-adoption.md) | Serena MCP 서버 도입 및 Claude Code 병행 전략 | Accepted | Done | 2026-03-18 |
| [003](003-response-request-pattern.md) | Response/Request 패턴 설계 | Accepted | Done | 2025-03~09 |
| [004](004-dto-entity-responsibility.md) | DTO/Entity 책임 재정의 | Accepted | Done | 2025-07 |
| [005](005-poetry-to-uv.md) | Poetry에서 uv로 전환 | Accepted | Done | 2025-04 |
| [006](006-ddd-layered-architecture.md) | 도메인별 레이어드 아키텍처 전환 | Accepted | Done | 2025-07~08 |
| [007](007-di-container-and-app-separation.md) | DI 컨테이너 계층화와 Interface별 앱 분리 | Accepted | Done | 2025-09~11 |
| [008](008-deploy-env-separation.md) | 배포 환경 분리 및 설정 관리 | Accepted | Done | 2025-09 |
| [009](009-async-external-clients.md) | 비동기 외부 클라이언트 표준화 | Accepted | Done | 2025-10 |
| [010](010-code-quality-tools.md) | 코드 품질 도구 체계화 | Accepted | Done | 2025-10 |

## 미래 고려 사항 (Open Issues)

| 이슈 | 제목 | 라벨 |
|------|------|------|
| #8 | websocket router 문서화 라이브러리 추가 | enhancement |
| #11 | pytest 추가하기 | enhancement |
| #12 | locust 추가하기 | enhancement |
| #13 | auth 기능 추가 | enhancement |
| #18 | database health check | enhancement |
| #28 | serverless 추가 | enhancement |
| #29 | DB 환경별 분리 | enhancement, refactor |
| #31 | message broker별 환경 분리 | enhancement, refactor |
| #32 | 로깅 | enhancement |
| #33 | 3 tier architecture로 변경 | refactor |
| #35 | 데이터 CRUD 유효성 검사 추가 | - |
| #36 | vector db 추가하기 | enhancement |
| #45 | vercel 추가하기 | enhancement |
| #46 | dynamodb 추가 | enhancement |
| #47 | replex 도입 및 자체 admin 페이지 | enhancement |
| #51 | pydanticAI 도입 | enhancement |
| #52 | alembic 개발 환경별 분리 | refactor |
| #55 | error 발생시 slack, discord 알림 | enhancement |
| #58 | ruff 추가 | - |

## 작성 가이드

### 파일 네이밍
```
{번호}-{주제}.md
예: 001-celery-to-taskiq.md
```

### 문서 구조
```markdown
# {번호}. {제목}

- 상태: Accepted / Deprecated / Superseded by {번호}
- 날짜: YYYY-MM-DD
- 관련 이슈: #{번호}

## 배경
## 문제
## 검토한 대안
## 결정
## 근거
```

### 상태 값
- **Accepted** — 현재 적용 중
- **Deprecated** — 더 이상 유효하지 않음
- **Superseded by XXX** — 다른 결정으로 대체됨
