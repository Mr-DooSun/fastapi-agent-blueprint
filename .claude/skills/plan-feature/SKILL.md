---
name: plan-feature
description: |
  This skill should be used when the user asks to "기능 설계", "기능 계획",
  "plan feature", "설계해줘", "기능 기획", "아키텍처 설계", "design feature",
  or wants to plan and design a new feature before implementation.
---

# 기능 구현 계획 수립

설명: $ARGUMENTS

## 사전 준비

1. Serena `architecture_conventions` 메모리 읽기 — 현재 DO/DON'T 규칙 확인
2. Serena `refactoring_status` 메모리 읽기 — 현재 진행 중인 작업 확인
3. Serena `project_overview` 메모리 읽기 — 기술 스택 및 구조 확인
4. 현재 도메인 목록 파악:
   !`ls -d src/*/ 2>/dev/null | grep -v _core | grep -v _apps | sed 's|src/||;s|/||' || echo "(none)"`

## Phase 0: 요구사항 인터뷰

사용자에게 다음 카테고리에서 3~5개 질문을 한다.
`${CLAUDE_SKILL_DIR}/references/planning-checklists.md`의 "질문 은행"을 참고하되, 기능에 맞게 선별한다.

**필수 질문 카테고리**:
1. **데이터 모델** — 핵심 엔티티와 필드는 무엇인가?
2. **비즈니스 규칙** — 검증/제약 조건이 있는가?
3. **사용자 유형** — 누가 이 기능을 사용하는가? (인증 필요?)
4. **외부 연동** — 외부 API, 파일 저장소, 메시지 큐 사용 여부?
5. **비동기 처리** — 즉시 응답 vs. 백그라운드 처리 필요한 작업이 있는가?

사용자 응답을 받은 후, 다음을 정리한다:
- [ ] 기능 요구사항 체크리스트 (functional)
- [ ] 비기능 요구사항 (성능, 보안, 확장성)
- [ ] 식별된 엣지 케이스

## Phase 1: 아키텍처 영향 분석

### 1.1 레이어 영향 분석
각 레이어에 대해 변경/추가가 필요한지 판단:
- **Domain**: 새 DTO, Protocol, Service, Exception, Event 필요?
- **Application**: 새 UseCase 메서드 필요? 기존 UseCase 수정?
- **Infrastructure**: 새 Model, Repository, DI Container 필요? DB 마이그레이션?
- **Interface**: 새 Router, Request/Response DTO, Worker Task 필요?

### 1.2 도메인 영향 분석
- 기존 도메인 수정으로 충분한가? → 어떤 도메인의 어떤 레이어?
- 새 도메인이 필요한가? → 도메인명 제안 및 근거
- Serena `find_symbol`로 관련 기존 코드 탐색

### 1.3 DTO 결정
CLAUDE.md의 Write DTO 기준에 따라 판단:
- Request 필드 == Domain 필드? → 별도 DTO 불필요, Request 직접 전달
- Request 필드 != Domain 필드? → 별도 Create/Update DTO 생성 필요, 위치: `application/` 또는 `domain/dtos/`

### 1.4 도메인 간 의존성
- 새 기능이 기존 도메인 데이터를 참조하는가?
- Protocol 기반 DIP 필요? → `/add-cross-domain` 패턴 적용

## Phase 2: 보안 체크포인트

`${CLAUDE_SKILL_DIR}/references/planning-checklists.md`의 "보안 평가 매트릭스"에 따라 6개 항목 평가:

| 항목 | 해당 여부 | 필요 조치 |
|------|-----------|-----------|
| 인증/인가 | Y/N | |
| 결제 처리 | Y/N | |
| 데이터 변경 (CUD) | Y/N | |
| 외부 API 연동 | Y/N | |
| 민감 데이터 (PII) | Y/N | |
| 파일 업로드/다운로드 | Y/N | |

해당되는 항목이 있으면 구체적인 보안 요구사항을 도출한다.
**1개 이상 해당 시**: 사용자에게 보안 요구사항을 확인받은 후 다음 Phase로 진행한다.

## Phase 3: 태스크 분해

### 3.1 태스크 식별
Phase 1의 분석 결과를 기반으로 실행 가능한 태스크 단위로 분해한다.
각 태스크를 기존 Skill에 매핑한다 (`${CLAUDE_SKILL_DIR}/references/planning-checklists.md`의 "Skill 매핑 테이블" 참조):

| 태스크 유형 | 매핑 Skill | 예시 |
|------------|-----------|------|
| 새 도메인 생성 | `/new-domain {name}` | `/new-domain order` |
| API 엔드포인트 추가 | `/add-api {desc}` | `/add-api "order에 POST /orders 추가"` |
| 비동기 태스크 추가 | `/add-worker-task {domain} {task}` | `/add-worker-task order send_notification` |
| 도메인 간 연결 | `/add-cross-domain from:{a} to:{b}` | `/add-cross-domain from:order to:user` |
| 테스트 생성 | `/test-domain {domain} generate` | `/test-domain order generate` |
| 아키텍처 검증 | `/review-architecture {domain}` | `/review-architecture order` |
| **매핑 불가** | 수동 구현 | 외부 API 연동, 커스텀 미들웨어 등 |

### 3.2 감독 수준 판단
각 태스크에 대해 (`${CLAUDE_SKILL_DIR}/references/planning-checklists.md`의 "감독 수준 정의" 참조):
- **L1 (AI 위임)**: 기존 Skill 100% 매핑, 패턴이 명확한 경우
- **L2 (확인 후 위임)**: 비즈니스 로직 판단, 새 도메인 필드 구성 등
- **L3 (감독 필수)**: 보안 관련, 결제 처리, 외부 API 연동, DB 설계 결정

### 3.3 실행 순서 및 병렬화
- 의존성 그래프 작성 (어떤 태스크가 다른 태스크에 선행되어야 하는지)
- 병렬 실행 가능한 태스크 그룹 식별
- 크리티컬 패스 식별

## 출력: 기능 구현 계획서

위 Phase 0~3의 결과를 아래 형식으로 정리하여 사용자에게 제시한다
(`${CLAUDE_SKILL_DIR}/references/planning-checklists.md`의 "출력 계획서 템플릿" 참조):

```
# 기능 구현 계획: {Feature Name}

## 1. 요구사항 요약
(Phase 0 결과)

## 2. 아키텍처 영향 분석
(Phase 1 결과 — 레이어별 변경사항 표)

## 3. 보안 평가
(Phase 2 결과 — 보안 매트릭스 표)

## 4. 실행 태스크 목록
| # | 태스크 | Skill | 감독 수준 | 선행 태스크 | 병렬 그룹 |
|---|--------|-------|----------|------------|----------|
(Phase 3 결과)

## 5. 실행 순서
(의존성 그래프 텍스트 표현)

## 6. 검증 계획
- /review-architecture {domain} 실행
- /test-domain {domain} generate → run 실행
- pre-commit 전체 실행
```

## 계획 승인 후

사용자가 계획을 승인하면:
1. 첫 번째 태스크부터 순서대로 실행을 제안한다
2. 각 태스크 실행 전 해당 Skill을 안내한다
3. "L3 감독 필수" 태스크는 실행 전 사용자 확인을 받는다
