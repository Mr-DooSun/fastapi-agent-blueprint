---
name: fix-bug
argument-hint: "bug description or issue number"
description: |
  This skill should be used when the user asks to "버그 수정",
  "fix bug", "이슈 해결", "에러 수정", "오류 수정", "문제 해결",
  "debug", "troubleshoot", "에러 추적",
  or reports a specific bug or error that needs investigation and fixing.
---

# 버그 수정 워크플로우

버그 설명: $ARGUMENTS

## Phase 1: 재현 (Reproduce)
1. 버그 설명을 분석하여 영향받는 도메인과 레이어 파악
2. GitHub 이슈 번호가 있으면 `gh issue view {number}`로 상세 내용 확인
3. 재현 가능한 테스트 케이스가 있는지 기존 테스트에서 확인
4. 재현 테스트가 없으면 먼저 작성 (red 상태 확인)

## Phase 2: 추적 (Trace)
1. Serena `refactoring_status` 메모리 읽기 — 현재 아키텍처 상태 확인
2. Serena `find_symbol`로 관련 코드 위치 파악
2. 호출 경로 추적: Router → UseCase → Service → Repository
3. 변환 경계 점검:
   - Request → UseCase 전달 시 데이터 손실 없는지
   - Model → DTO 변환 시 필드 매핑 올바른지
   - DTO → Response 변환 시 제외할 필드가 맞는지
4. DI 와이어링 점검:
   - 올바른 구현체가 주입되는지
   - Singleton/Factory 구분이 맞는지

## Phase 3: 수정 (Fix)
1. 가장 낮은 레이어에서 수정 (domain > infrastructure 선호)
2. 기존 패턴을 따라 수정 — 새로운 패턴 도입 금지 (변환: **project-dna.md §6**, Router: **§9** 참조)
3. CLAUDE.md 절대 금지 규칙 준수 확인

## Phase 4: 검증 (Verify)
1. Phase 1에서 작성한 재현 테스트가 통과하는지 확인 (green)
2. 기존 테스트가 깨지지 않는지 확인:
   ```bash
   pytest tests/unit/{domain}/ tests/integration/{domain}/ -v
   ```
3. pre-commit 훅 실행:
   ```bash
   pre-commit run --files {변경된 파일들}
   ```

## Phase 5: 커밋 (Commit)
커밋 컨벤션: `[#{issue}] {type}: {description}`

타입:
- `fix` — 버그 수정
- `feat` — 새 기능
- `refactor` — 리팩토링
- `test` — 테스트 추가/수정
- `docs` — 문서
- `chore` — 기타

사용자에게 커밋 메시지를 제안하고 확인 받은 후 커밋한다.
