---
name: security-review
argument-hint: "domain_name, file_path, or all"
description: |
  This skill should be used when the user asks to "보안 리뷰",
  "보안 검사", "security review", "보안 감사", "OWASP 검사",
  "security audit", or wants to audit code security for a domain or file.
---

# OWASP 기반 코드 보안 감사

대상: $ARGUMENTS (도메인명, 파일 경로, 또는 "all")

## 감사 대상
- "all"인 경우 `src/` 하위의 모든 디렉토리를 대상으로 한다 (`_core`, `_apps` 포함).
- 특정 도메인명인 경우 `src/{name}/` 만 대상으로 한다.
- 파일 경로인 경우 해당 파일만 대상으로 한다.

## 현재 도메인 목록
!`ls -d src/*/ 2>/dev/null | sed 's|src/||;s|/||' || echo "(none)"`

## 감사 절차

6개 보안 카테고리, 총 24+ 항목을 Grep 기반으로 검사한다.
상세 체크리스트는 `${CLAUDE_SKILL_DIR}/references/security-checklist.md`를 참조한다.

**카테고리 요약**:
1. **Injection 방지** — SQL, Command, Template injection 패턴
2. **인증/인가** — 엔드포인트 보호, 자격 증명 관리, JWT, RBAC
3. **데이터 보호** — PII 노출, 로그 내 민감정보, 암호화
4. **입력 검증** — Pydantic 검증, 파일 업로드, Path Traversal
5. **의존성/설정** — 취약 패키지, 디버그 모드, CORS, 시크릿 관리
6. **에러 처리/로깅** — 스택 트레이스 노출, Rate Limiting

## 감사 실행 방법

체크리스트의 각 항목은 `[항상]` 또는 `[해당 시]`로 분류되어 있다:

### 조건부 검사 절차
1. `[항상]` 항목: 무조건 Grep 검사 실행
2. `[해당 시]` 항목: 먼저 탐지 조건(해당 기능의 import/사용 여부)을 Grep으로 확인
   - 기능 미사용 → `[SKIP]` 출력 후 건너뜀
   - 기능 사용 중 → 상세 검사 진행
3. 위양성(false positive) 필터링 — 테스트 코드, 주석, 설정 예시 제외
4. 발견된 이슈에 구체적 파일/라인 정보 포함
5. 심각도 표시: [CRITICAL], [HIGH], [MEDIUM], [LOW]

## 출력 형식

```
=== OWASP 코드 보안 감사 결과 ===

--- 1. Injection 방지 ---
[PASS] SQL injection: f-string SQL 패턴 없음
[FAIL][HIGH] Command injection: subprocess.call(shell=True) 발견
     → 파일: src/example/infrastructure/services/export_service.py:42
     → 권장: subprocess.run(shell=False) + shlex.split() 사용

--- 2. 인증/인가 ---
[PASS] 하드코딩된 자격 증명 없음
[FAIL][CRITICAL] 엔드포인트 인증 누락: POST /user에 auth dependency 없음
     → 파일: src/user/interface/server/routers/user_router.py:19
     → 권장: Depends(get_current_user) 추가

...

=== 요약 ===
통과: XX/24 | 실패: XX/24 | 건너뜀: XX/24
  - CRITICAL: X건
  - HIGH: X건
  - MEDIUM: X건
  - LOW: X건
  - SKIP: X건 (해당 기능 미사용)
```

## 외부 도구 연동 (선택)
해당 도구가 설치된 경우 추가 실행:
```bash
# Python 보안 정적 분석
bandit -r src/{name}/ -f json 2>/dev/null || echo "bandit 미설치"

# 의존성 취약점 검사
pip audit 2>/dev/null || uv pip audit 2>/dev/null || echo "audit tool 미설치"
```

## 실패 시 권장 조치
- Injection → parameterized query, shell=False, Jinja2 autoescape
- 인증 누락 → Depends(get_current_user) 또는 RBAC middleware 추가
- PII 노출 → model_dump(exclude={'password', ...}) 적용
- 하드코딩 시크릿 → Settings 클래스(환경변수) 이전
- CORS 와일드카드 → production에서 특정 origin으로 제한
- 스택 트레이스 노출 → is_dev 조건 확인 (ExceptionMiddleware 패턴)
