---
name: review-architecture
argument-hint: domain_name or all
description: |
  This skill should be used when the user asks to "아키텍처 리뷰",
  "아키텍처 검사", "review architecture", "컴플라이언스 감사",
  or wants to audit architecture compliance for a domain.
---

# 아키텍처 컴플라이언스 감사

대상: $ARGUMENTS (도메인명 또는 "all")

## 감사 대상
"all"인 경우 `src/` 하위의 모든 도메인 디렉토리를 대상으로 한다 (`_core`, `_apps` 제외).
특정 도메인명인 경우 `src/{name}/` 만 대상으로 한다.

## 현재 도메인 목록
!`ls -d src/*/ 2>/dev/null | grep -v _core | grep -v _apps | sed 's|src/||;s|/||' || echo "(none)"`

## 감사 절차

6개 카테고리, 총 20+ 항목을 Grep 기반으로 검사한다.
상세 체크리스트는 `${CLAUDE_SKILL_DIR}/references/checklist.md`를 참조한다.

**카테고리 요약**:
1. **레이어 의존성 규칙** — domain → infrastructure/interface import 위반
2. **변환 패턴 준수** — to_entity/from_entity/Mapper 사용 여부
3. **DTO/Response 무결성** — 다중상속, 민감 필드 노출
4. **DI Container 정확성** — Singleton/Factory 구분
5. **테스트 커버리지** — 필수 테스트 파일 존재 여부
6. **Bootstrap 와이어링** — 앱 레벨 등록 여부

## 출력 형식

```
[PASS] 레이어 의존성: domain → infrastructure import 없음
[FAIL] 테스트 커버리지: tests/unit/{name}/domain/test_{name}_service.py 누락
       → 권장: `/test-domain {name} generate`로 생성
```

최종 요약: `통과: XX/20 | 실패: XX/20`

## 실패 시 권장 조치
- 레이어 의존성 위반 → Protocol 기반으로 변경
- 변환 패턴 위반 → 인라인 변환으로 교체 (model_dump, model_validate)
- 테스트 누락 → `/test-domain {name} generate` 실행
- Bootstrap 미등록 → `/new-domain` 레퍼런스의 Layer 5 참고
