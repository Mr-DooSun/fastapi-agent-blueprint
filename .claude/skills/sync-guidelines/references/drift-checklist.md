# 가이드라인 동기화 점검 항목 상세

## 1. CLAUDE.md ↔ 코드 일치 확인

CLAUDE.md를 읽고 각 섹션을 실제 코드와 대조:

- [ ] **절대 금지 규칙**: 실제로 위반 사례가 없는지 Grep으로 확인
  - `from src.*.infrastructure` in domain/ 파일
  - `to_entity(` 또는 `from_entity(` 호출
  - `class.*Mapper` 정의
  - Response/Request 다중상속 패턴
- [ ] **변환 패턴**: CLAUDE.md에 기술된 4가지 패턴이 실제 코드에서 동일하게 사용되는지
  - Request → Service: `entity=item` 직접 전달
  - Model → DTO: `model_validate(model, from_attributes=True)`
  - DTO → Response: `model_dump(exclude={...})`
- [ ] **Write DTO 기준**: 현재 Request/DTO 사용 방식이 기준과 일치하는지

## 2. Skills ↔ 코드 일치 확인

각 스킬의 SKILL.md를 읽고 레퍼런스 코드와 대조:

- [ ] **`/new-domain`**: 파일 목록이 `src/user/` 실제 구조와 일치하는지
  - 새로 추가된 파일이 Skills에 반영되지 않았는지
  - 삭제된 파일이 Skills에 여전히 남아있는지
  - import 경로가 실제 base class 위치와 일치하는지
  - 클래스 시그니처 (Generic 타입 파라미터 등)가 일치하는지
- [ ] **`/add-api`**: 구현 순서와 패턴이 현재 코드와 일치하는지
  - Router 데코레이터 패턴 (`@inject`, `Depends(Provide[...])`)
  - SuccessResponse 사용 패턴
- [ ] **`/add-worker-task`**: 태스크 패턴이 현재 broker 설정과 일치하는지
  - `@broker.task` 데코레이터 사용법
  - DI wiring 패턴
- [ ] **`/review-architecture`**: 체크항목이 현재 규칙을 모두 포함하는지
- [ ] **`/test-domain`**: 테스트 패턴이 실제 테스트 코드와 일치하는지
- [ ] **`/add-cross-domain`**: Protocol 기반 의존성 패턴이 현재와 일치하는지

## 3. Serena 메모리 ↔ 현재 상태 확인

Serena 메모리를 읽고 현재 코드와 대조:

- [ ] **`architecture_conventions`**: DO/DON'T 규칙이 CLAUDE.md 및 실제 코드와 일치하는지
- [ ] **`refactoring_status`**: 현재 진행 상황이 정확한지
- [ ] **`project_overview`**: 기술 스택, 엔트리 포인트 등이 최신인지

## 4. project-dna.md ↔ 코드 일치 확인

`.claude/skills/_shared/project-dna.md`의 각 섹션을 실제 코드와 대조:

- [ ] **레이어 구조**: project-dna.md §1의 디렉토리 구조가 `src/user/` 실제 구조와 일치하는지
  - Serena `get_symbols_overview` 또는 Glob `src/user/**/*.py` 결과와 대조
- [ ] **Base class 경로**: §2의 모든 import 경로가 실제 파일 위치와 일치하는지
  - 각 경로에 대해 해당 모듈에서 클래스 import 가능 확인
- [ ] **Generic 타입**: §3의 시그니처가 현재 Base class 정의와 일치하는지
  - `BaseRepositoryProtocol`, `BaseRepository`, `SuccessResponse` 클래스 정의 확인
- [ ] **CRUD 메서드**: §4의 `BaseRepositoryProtocol` 메서드 목록이 최신인지
  - Serena `get_symbols_overview` → 메서드 목록 비교
- [ ] **DI 패턴**: §5의 Singleton/Factory 매핑이 현재 `UserContainer` 코드와 일치하는지
- [ ] **변환 패턴**: §6의 `model_validate`/`model_dump` 사용법이 현재와 일치하는지
- [ ] **보안 도구**: §7의 도구 목록이 `pyproject.toml`과 `.pre-commit-config.yaml`과 일치하는지
  - 특히 bandit skip 목록, flake8 ignore 목록 확인
- [ ] **활성 기능**: §8의 기능 상태가 최신인지
  - Grep으로 `jwt`, `UploadFile`, `RBAC`, `slowapi` 등 import 존재 여부 확인
- [ ] **상속 체인**: §2의 BaseRequest/BaseResponse 부모 클래스가 정확한지
  - `ApiConfig` → `BaseModel` 체인 확인

## 5. References ↔ 코드 일치 확인

각 Skill의 references/ 파일 자체 콘텐츠가 현재 코드와 일치하는지 점검한다.
(project-dna.md 포인터 참조 부분은 섹션 4에서 이미 검증됨)

### 자동 검증 (Glob/Grep 기반 — [AUTO-FIX] 대상)

- [ ] **`new-domain` 파일 목록** (`scaffolding-layers.md`):
  - `Glob src/user/**/*.py` 결과에서 `__init__.py` 제외
  - scaffolding-layers.md의 번호 목록(1~26)에서 `src/{name}/` 경로 추출
  - `{name}` → `user`로 치환하여 양쪽 비교
  - 차이 발견 시: 누락 파일은 적절한 Layer 섹션에 추가 제안, 삭제된 파일은 제거 제안

- [ ] **`test-domain` Factory 패턴** (`test-patterns.md`):
  - `tests/factories/user_factory.py`를 읽어 함수 목록 추출 (def 라인)
  - test-patterns.md의 코드 블록에서 함수 시그니처 추출
  - 함수명/파라미터/import 경로가 일치하는지 비교
  - 차이 발견 시: user_factory.py 기준으로 코드 블록 갱신 제안

- [ ] **`plan-feature` Skill 매핑** (`planning-checklists.md`):
  - `Glob .claude/skills/*/SKILL.md`에서 각 파일의 `name:` 필드 수집
  - planning-checklists.md "3. Skill 매핑 테이블"의 "매핑 Skill" 열에서 `/스킬명` 추출
  - 양쪽 집합 비교 (추가/삭제/이름 변경)
  - 차이 발견 시: 테이블에 행 추가/삭제 제안

### 수동 확인 (변경 이력 기반 — [REVIEW] 대상)

- [ ] **`review-architecture` 체크리스트** (`checklist.md`):
  - CLAUDE.md "절대 금지 규칙" 섹션의 항목 수를 세어 checklist.md의 관련 검사 항목 수와 대조
  - 항목 수 불일치 시: 새 규칙에 대한 Grep 패턴 추가 필요 여부 사용자에게 확인

- [ ] **`security-review` 보안 체크리스트** (`security-checklist.md`):
  - project-dna.md §8의 "활성" 기능 목록 추출
  - security-checklist.md에서 `[해당 시]` 마킹된 항목의 기능 목록 추출
  - 새로 활성화된 기능에 대한 보안 검사 항목 존재 여부 확인
  - 미커버 기능 발견 시: 해당 기능의 보안 검사 항목 추가 필요 여부 사용자에게 확인
