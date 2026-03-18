# FastAPI Layered Architecture - Claude 작업 가이드

## 프로젝트 스케일
이 프로젝트는 도메인 10개 이상, 팀원 5명 이상의 엔터프라이즈급 서비스를 목표로 설계한다.
모든 제안과 설계는 이 규모를 전제로 확장성, 유지보수성, 팀 협업을 고려해야 한다.

## 작업 전 필수 확인
1. Serena `refactoring_status` 메모리로 현재 Phase 확인
2. Serena `architecture_conventions` 메모리로 DO/DON'T 확인

## 절대 금지 규칙
- Domain 레이어에서 Infrastructure import 금지
- 다중상속 패턴 금지: `class Response(BaseResponse, Entity)`
- `to_entity()`, `from_entity()` 메서드 사용 금지
- Model 객체를 Repository 밖으로 노출 금지
- Mapper 클래스 별도 생성 금지 (인라인 변환으로 충분)

## 변환 패턴
- Request → Service: `item` 직접 전달 (필드가 동일한 경우)
- Request → 별도 DTO: `CreateNameDTO(**item.model_dump(), extra_field=...)` (필드가 다른 경우)
- Model → DTO: `UserDTO.model_validate(model, from_attributes=True)`
- DTO → Response: `UserResponse(**dto.model_dump(exclude={'password'}))`

## Write DTO 생성 기준
- Request 필드와 동일한 경우: Request를 직접 레이어 DTO로 사용, 별도 Create/Update DTO 불필요
- 필드가 다른 경우 (auth context 주입, 파생 필드 등): `application/` 또는 `domain/dtos/`에 별도 DTO 생성

## 작업별 Skills (slash commands)
- `/plan-feature {description}` — 기능 구현 계획 수립 (요구사항 인터뷰 → 아키텍처 분석 → 보안 체크 → 태스크 분해)
- `/new-domain {name}` — 도메인 전체 스캐폴딩 (28개 파일 + 테스트)
- `/add-api {description}` — 기존 도메인에 API 엔드포인트 추가
- `/add-worker-task {domain} {task}` — 비동기 Taskiq 태스크 추가
- `/add-cross-domain from:{a} to:{b}` — 도메인 간 의존성 연결
- `/review-architecture {domain|all}` — 아키텍처 컴플라이언스 감사
- `/security-review {domain|file|all}` — OWASP 기반 코드 보안 감사
- `/test-domain {domain} [generate|run]` — 테스트 생성 또는 실행
- `/fix-bug {description}` — 구조화된 버그 수정 워크플로우
- `/sync-guidelines` — 설계 변경 후 가이드라인 동기화 + project-dna.md 재생성
- `/migrate-domain {generate|upgrade|downgrade|status}` — Alembic 마이그레이션 관리

## 도메인 자동 발견
- `src/_core/infrastructure/discovery.py`의 `discover_domains()`가 도메인을 자동 탐지
- Server/Worker의 App-level Container는 `DynamicContainer` + 팩토리 함수 사용
- **새 도메인 추가 시 `container.py`, `bootstrap.py` 수정 불필요** (자동 등록)
- 도메인 Container 자체는 `DeclarativeContainer` 유지

## 도구 선택 기준

### 코드 탐색/읽기 (우선순위 순)
1. **Serena 심볼 도구** (기본): `get_symbols_overview` → `find_symbol(include_body=True)`
   - 파일 구조 파악, 특정 메서드 읽기, 클래스 계층 탐색
   - 토큰 효율이 높아 대규모 코드베이스에서 필수
2. **Grep/Glob** (보조): 파일 위치 찾기, 문자열 패턴 검색, 설정 파일 탐색
3. **Read** (최후 수단): 비코드 파일, 설정 파일, 또는 심볼 탐색으로 불충분할 때만

### 영향 범위 분석
- 리팩토링/시그니처 변경 시: Serena `find_referencing_symbols` 우선
- 단순 문자열 검색: Grep

### 편집
- 심볼 전체 교체 (메서드, 클래스): Serena `replace_symbol_body`
- 부분 수정 (몇 줄 변경): Claude Code `Edit`
- 새 코드 삽입: Serena `insert_before/after_symbol` 또는 `Edit`

### 정형화된 작업
- 도메인 생성/API 추가/테스트 등: Skills (`/new-domain`, `/add-api` 등)

### 라이브러리 문서
- context7으로 최신 문서 확인 (SQLAlchemy 2.0, Pydantic 2.x, Taskiq 등)
