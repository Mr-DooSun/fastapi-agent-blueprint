---
name: sync-guidelines
disable-model-invocation: true
description: |
  This skill should be used when the user asks to "가이드라인 동기화",
  "sync guidelines", "문서 점검", "스킬 업데이트 확인",
  "project-dna 갱신", "패턴 동기화", "코드-문서 일치 확인",
  or after architecture changes to verify Skills/CLAUDE.md match the actual code.
---

# 가이드라인 동기화 점검

설계 변경 후 CLAUDE.md, Skills, Serena 메모리가 실제 코드와 일치하는지 점검한다.

## 레퍼런스 코드 분석
`src/user/`를 기준 도메인으로 읽어서 현재 실제 패턴을 파악한다:
- Base class import 경로
- 클래스 상속 구조
- 변환 패턴 (Model→DTO, DTO→Response)
- DI 패턴 (Singleton/Factory)
- 파일 구조

## 점검 대상 (3개 카테고리)
1. **CLAUDE.md ↔ 코드** — 절대 금지 규칙, 변환 패턴, Write DTO 기준
2. **Skills ↔ 코드** — 각 스킬의 SKILL.md가 현재와 일치하는지 (references는 Phase 5에서 별도 점검)
3. **Serena 메모리 ↔ 코드** — architecture_conventions, refactoring_status, project_overview

상세 점검 항목은 `${CLAUDE_SKILL_DIR}/references/drift-checklist.md`를 참조한다.

## 출력 형식

```
=== 가이드라인 동기화 점검 결과 ===

[OK] CLAUDE.md: 절대 금지 규칙 — 위반 없음
[DRIFT] /new-domain: Base class import — 경로 변경 감지
  → 기존: src._core.infrastructure.database.base_repository
  → 실제: src._core.database.base_repository
  → 조치: .claude/skills/new-domain/references/scaffolding-layers.md 업데이트 필요

동기화 필요: X건 / 전체: Y건
```

## DRIFT 발견 시 조치
1. 발견된 불일치 목록을 사용자에게 보여준다
2. 각 불일치에 대해 수정 제안을 한다
3. 사용자 승인 후 해당 파일을 업데이트한다
4. 업데이트 완료 후 다시 점검하여 모든 항목이 [OK]인지 확인한다

## Phase 4: project-dna.md 재생성

DRIFT가 발견되거나 사용자가 요청하면 `.claude/skills/_shared/project-dna.md`를 재생성한다.

### 재생성 절차
1. `src/user/`를 레퍼런스 도메인으로 Serena `get_symbols_overview`로 스캔
2. `src/_core/` Base 클래스 시그니처 추출:
   - import 경로 (모든 Base class의 실제 파일 위치)
   - Generic 파라미터 (TypeVar 바운드, 클래스 정의)
   - `__init__` 시그니처 (BaseRepository 등)
   - 메서드 목록 (BaseRepositoryProtocol)
3. DI 패턴 추출: 각 Container의 `providers.Singleton` / `providers.Factory` 매핑 확인
4. 보안 도구 스캔: `pyproject.toml`과 `.pre-commit-config.yaml`에서 활성 도구 목록 추출
5. 활성 기능 스캔: 코드베이스에서 `jwt`, `UploadFile`, `RBAC`, `slowapi`, `websocket` import 존재 여부 확인
6. `.claude/skills/_shared/project-dna.md` 파일을 최신 정보로 재생성 (날짜 갱신)
7. 각 Skill의 references/ 파일과 project-dna.md 비교 → 불일치 항목 보고
8. Serena `architecture_conventions` 메모리 업데이트 (변경사항 반영)

## Phase 5: References Drift 점검

project-dna.md 재생성 완료 후, 각 Skill의 references/ 파일이 현재 코드와 일치하는지 점검한다.
상세 점검 항목은 `${CLAUDE_SKILL_DIR}/references/drift-checklist.md`의 "5. References ↔ 코드" 섹션을 따른다.

### 자동 검증 ([AUTO-FIX] 대상)
코드에서 기계적으로 추출 가능한 항목. drift 발견 시 수정 diff를 생성하여 사용자에게 제시한다.

1. **파일 목록** (`new-domain/references/scaffolding-layers.md`)
   - `Glob src/user/**/*.py` 결과와 scaffolding-layers.md의 파일 목록(1~26번) 대조
   - 누락/삭제된 파일 탐지

2. **Factory 패턴** (`test-domain/references/test-patterns.md`)
   - `tests/factories/user_factory.py`를 읽고 test-patterns.md의 코드 블록과 비교
   - 함수 시그니처, import 경로 변경 탐지

3. **Skill 매핑** (`plan-feature/references/planning-checklists.md`)
   - `.claude/skills/*/SKILL.md`에서 `name:` 필드 수집
   - planning-checklists.md "Skill 매핑 테이블"의 Skill 열과 대조

### 수동 확인 ([REVIEW] 대상)
정책/표준 기반 콘텐츠. 관련 소스가 변경되었는지만 감지하고 사용자에게 검토를 요청한다.

4. **아키텍처 체크리스트** (`review-architecture/references/checklist.md`)
   - CLAUDE.md 절대 금지 규칙 항목 수 vs. checklist.md 검사 항목 수 대조
   - 불일치 시 새 규칙에 맞는 Grep 패턴 추가 필요 여부 확인 요청

5. **보안 체크리스트** (`security-review/references/security-checklist.md`)
   - project-dna.md §8 활성 기능 상태와 `[해당 시]` 항목 대조
   - 새로 활성화된 기능에 보안 검사 항목이 있는지 확인 요청

### Phase 5 출력 형식

```
--- References Drift 점검 ---

[AUTO-FIX] scaffolding-layers.md: 파일 목록
  → 추가 필요: src/{name}/domain/events/__init__.py
  → 수정 제안 생성됨 — 적용하시겠습니까?

[OK] test-patterns.md: Factory 패턴 — 변경 없음
[OK] planning-checklists.md: Skill 매핑 — 변경 없음

[REVIEW] security-checklist.md: 활성 기능 변경 감지
  → project-dna.md §8에서 "JWT/Authentication" 활성 전환됨
  → [해당 시] 항목에 JWT 관련 보안 검사 추가 필요한지 확인해주세요

References: AUTO-FIX X건 | REVIEW X건 | OK X건
```

### 재생성 후 검증
- project-dna.md의 모든 import 경로가 실제 파일과 일치하는지 `Grep`으로 확인
- 생성된 Generic 시그니처가 소스 코드 정의와 일치하는지 비교

## 언제 실행해야 하는가
- 아키텍처 리팩토링 후
- Base class나 공통 모듈 변경 후
- 새로운 패턴이나 컨벤션 도입 후
- project-dna.md 갱신일 2주 이상 경과 시
- 주기적 점검 (2주에 1회 권장)
