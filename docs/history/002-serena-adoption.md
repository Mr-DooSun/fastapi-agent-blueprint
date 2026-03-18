# 002. Serena MCP 서버 도입 및 Claude Code 병행 전략

- 상태: Accepted
- 날짜: 2026-03-18
- 관련 이슈: #57

## 배경

프로젝트가 DDD 기반 모듈형 레이어드 아키텍처로 성장하면서, AI 코딩 도구의 코드 탐색 정확도가 중요해졌다.
Claude Code의 Grep/Glob 기반 텍스트 검색만으로는 클래스 계층, 메서드 시그니처, 참조 관계를 구조적으로 파악하기 어려웠다.

특히 다음 작업에서 한계가 드러났다:
- 도메인 간 Protocol 기반 의존성 추적 (어떤 클래스가 어떤 Protocol을 구현하는지)
- BaseRepository의 Generic 타입 파라미터 확인 (상속 체인 추적)
- 리팩토링 시 영향 범위 분석 (find_referencing_symbols)

## 문제

### Claude Code 텍스트 검색의 한계

```
Grep: "class UserRepository" → 텍스트 매칭 (파일:줄 번호)
  - 상속 구조 모름
  - 어떤 메서드가 있는지 모름
  - 누가 이 클래스를 참조하는지 모름

Serena: find_symbol "UserRepository" → AST 수준 이해
  - BaseRepository[BaseModel, UserDTO, BaseModel] 상속 확인
  - 메서드 목록 + 시그니처 구조적 파악
  - find_referencing_symbols로 모든 참조 추적
```

### 팀 지식 공유의 부재

Claude Code auto-memory는 `~/.claude/projects/` 에 머신 로컬로 저장되어 팀 공유가 불가능했다.
리팩토링 진행 상태, 아키텍처 컨벤션 같은 팀 공유 지식을 저장할 수단이 없었다.

## 검토한 대안

### 1. Claude Code 단독 사용 (Grep/Glob + auto-memory)
- 텍스트 검색으로 대부분의 작업 가능
- 심볼 수준 탐색 불가 → 리팩토링, 영향 분석에 약함
- 메모리가 머신 로컬 → 팀 공유 불가

### 2. Serena 단독 사용
- LSP 기반 심볼 탐색 + 메모리 시스템 제공
- 스킬 시스템, 훅 시스템 없음 → 자동화 워크플로우 구축 불가
- 파일 수준 편집 도구가 Claude Code보다 제한적

### 3. Claude Code + Serena 병행 사용
- Claude Code: 스킬 시스템, 훅 시스템, Grep/Glob 텍스트 검색, auto-memory
- Serena: LSP 심볼 탐색, 팀 공유 메모리 (.serena/ git 커밋)
- 각 도구의 강점을 조합

## 결정

**Claude Code + Serena 병행 사용 채택**

### 4계층 메모리 아키텍처

| 계층 | 저장소 | 공유 | 역할 | 업데이트 주체 |
|------|--------|------|------|-------------|
| CLAUDE.md | 프로젝트 루트 | git (팀) | 불변 팀 규칙 | 수동 (사람) |
| project-dna.md | .claude/skills/_shared/ | git (팀) | 코드에서 추출된 패턴 레퍼런스 | /sync-guidelines (자동) |
| Serena memories | .serena/memories/ | git (팀) | 동적 프로젝트 상태 + 심볼 탐색 컨텍스트 | /sync-guidelines + 수동 |
| Claude auto-memory | ~/.claude/projects/ | 로컬 (개인) | 세션 피드백, 개인 학습 | Claude 자동 |

### 도구 역할 분리

```
코드 탐색:
  1순위 — Serena 심볼 도구 (get_symbols_overview, find_symbol, find_referencing_symbols)
  2순위 — Grep/Glob (텍스트 패턴 검색, 설정 파일)
  3순위 — Read (비코드 파일, 심볼 탐색으로 불충분할 때)

코드 편집:
  심볼 전체 교체 — Serena replace_symbol_body
  부분 수정 — Claude Code Edit
  새 코드 삽입 — Serena insert_before/after_symbol 또는 Edit

자동화:
  스킬 시스템 — Claude Code (.claude/skills/)
  훅 시스템 — Claude Code (.claude/settings.local.json)
  보안 검사 — Claude Code PreToolUse 훅

메모리:
  팀 공유 동적 상태 — Serena (.serena/memories/, git 커밋)
  개인 피드백 — Claude Code auto-memory (머신 로컬)
```

### Serena 메모리 구성 (4건)

| 메모리 | 역할 | 고유 정보 |
|--------|------|-----------|
| architecture_conventions | 심볼 탐색 전 컨텍스트 프라이밍 | 데이터 흐름도, 객체 역할 (DTO/Model/Schema 위치) |
| refactoring_status | 진행 중인 아키텍처 변경 추적 | Phase별 완료 상태, 위반 검사 결과 |
| project_overview | 프로젝트 수준 컨텍스트 | 목적, 앱 엔트리포인트, 의존성 방향 |
| suggested_commands | 개발자 CLI 참조 | 실행/테스트/린트/마이그레이션 명령어 |

### 자동 동기화 메커니즘

```
코드 변경 시:
  PostToolUse 훅 → 핵심 파일(src/_core/ 등) 변경 감지 → 경고 출력
  Stop 훅 → 세션 종료 전 /sync-guidelines 미실행 감지 → block → 자동 실행 강제
  /sync-guidelines → project-dna.md 재생성 + Serena 메모리 갱신
```

## 근거

| 기준 | Claude Code 단독 | Serena 단독 | Claude Code + Serena |
|------|-----------------|-------------|---------------------|
| 심볼 수준 탐색 | 불가 (Grep만) | 강함 (LSP) | 강함 |
| 스킬/훅 자동화 | 강함 | 없음 | 강함 |
| 팀 공유 메모리 | 불가 (로컬만) | 가능 (.serena/ git) | 가능 |
| 개인 학습 메모리 | 가능 | 제한적 | 가능 |
| 코드 편집 도구 | 강함 (Edit/Write) | 있음 (심볼 기반) | 상호 보완 |

1. 두 도구는 **다른 패러다임**으로 동작하므로 충돌이 아니라 보완
2. Serena의 핵심 가치는 메모리가 아니라 **LSP 기반 심볼 탐색** — 이는 Claude Code에 없는 기능
3. `.serena/`를 git에 커밋하면 **팀 공유 가능한 유일한 동적 지식 저장소** 역할
4. 역할을 명확히 분리하면 중복 없이 각 도구의 강점을 최대화

### 10+ 도메인 확장 시 진화 방향

- `domain_dependencies` 메모리 추가 (도메인 간 Protocol 의존성 맵)
- `active_work` 메모리 추가 (5+ 팀원 시 작업 현황 추적)
- 메모리 총 10개 이하 유지 (도구 호출 비용 관리)

### Serena가 불필요해지는 경우
- Claude Code가 LSP 기반 심볼 탐색을 네이티브로 지원할 때
- Claude Code auto-memory가 팀 공유를 지원할 때
- 프로젝트가 단일 도메인으로 축소되어 심볼 추적이 불필요할 때
