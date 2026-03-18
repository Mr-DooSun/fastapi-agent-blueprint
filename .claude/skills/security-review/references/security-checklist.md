# 보안 감사 체크리스트 상세

> **분류**: `[항상]` = 항상 검사 | `[해당 시]` = 해당 기능 사용 시만 검사 (미사용 시 [SKIP])
>
> **조건부 검사 자동 판별**: `[해당 시]` 항목의 활성 여부는
> `.claude/skills/_shared/project-dna.md` §8 "활성 기능" 테이블로 사전 판별한다.
> §8에서 "미구현"인 기능의 `[해당 시]` 항목은 Grep 없이 즉시 [SKIP] 처리한다.

## 1. Injection 방지 (Injection Prevention)
각 대상 Python 파일에 대해 Grep으로 검사:

### SQL Injection
- [ ] [항상][CRITICAL] `f"SELECT ` / `f"INSERT ` / `f"UPDATE ` / `f"DELETE ` 패턴 없음
  - Grep: `f["'].*\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b`
- [ ] [항상][CRITICAL] `.format()` + SQL 키워드 결합 없음
  - Grep: `\.format\(.*\).*(SELECT|INSERT|UPDATE|DELETE)`
- [ ] [항상][HIGH] `text()` 사용 시 파라미터 바인딩 적용 (f-string + text() 결합 금지)
  - Grep: `text\(f["']`
- [ ] [항상][MEDIUM] `exec()` / `eval()` 사용 없음
  - Grep: `\bexec\s*\(|\beval\s*\(`

### Command Injection
- [ ] [항상][CRITICAL] `subprocess.*(shell=True)` 사용 없음
  - Grep: `subprocess\.\w+\(.*shell\s*=\s*True`
- [ ] [항상][CRITICAL] `os.system(` 사용 없음
  - Grep: `os\.system\s*\(`
- [ ] [항상][HIGH] `os.popen(` 사용 없음
  - Grep: `os\.popen\s*\(`

### Template Injection
- [ ] [해당 시][MEDIUM] Jinja2 사용 시 `autoescape=True` 설정
  - 탐지 조건: `from jinja2` 또는 `Environment(` import 존재 시 검사 (project-dna.md §8에 미등록 — Grep으로 직접 확인)
  - Grep: `Environment\(` → autoescape 설정 확인

## 2. 인증/인가 (Authentication & Authorization)
router 파일 및 설정 파일에서 검사:

### 엔드포인트 보호
- [ ] [항상][CRITICAL] POST/PUT/DELETE 엔드포인트에 인증 dependency 존재
  - Grep: `@router\.(post|put|delete|patch)` → 해당 함수에 `Depends(.*auth|.*current_user|.*token)` 확인
  - 미구현 시: [FAIL] + "인증 미구현 — 프로덕션 배포 전 필수 구현" 경고
- [ ] [항상][HIGH] Admin 엔드포인트 접근 제한 확인
  - Grep: `interface/admin/` 파일에 인증 설정 확인

### 자격 증명 관리
- [ ] [항상][CRITICAL] 하드코딩된 password/secret/api_key/token 없음
  - Grep: `(password|secret|api_key|token)\s*=\s*["'][^"']{3,}["']`
  - 제외: Field(), os.environ, settings., getenv, 테스트 파일
- [ ] [해당 시][HIGH] JWT 설정 확인
  - 탐지 조건: **project-dna.md §8** "JWT/Authentication" 상태 확인 → "미구현"이면 [SKIP]
  - Grep: `algorithm.*=.*HS256` → RS256 권장 여부 확인
  - Grep: `exp.*timedelta` → 만료 시간 적절성 확인

### RBAC
- [ ] [해당 시][MEDIUM] 역할 기반 접근 제어 확인
  - 탐지 조건: **project-dna.md §8** "RBAC/Permissions" 상태 확인 → "미구현"이면 [SKIP]
  - router에서 role check dependency 사용 여부

## 3. 데이터 보호 (Data Protection)
DTO, Response, 로그 파일에서 검사:

### PII 노출 방지
- [ ] [항상][CRITICAL] Response DTO에 password 필드 미포함
  - Grep: `class.*Response` 블록에서 password 필드 없음
  - 또는: `model_dump(exclude=.*password)` 사용 확인
- [ ] [항상][HIGH] Response DTO에 민감 필드 미포함
  - 검사 대상: ssn, social_security, credit_card, card_number, secret, token, private_key
- [ ] [항상][HIGH] 로그에 PII 미포함
  - Grep: `(logger\.|logging\.|print\().*(password|secret|token|ssn|credit)`

### 암호화
- [ ] [해당 시][MEDIUM] 비밀번호 해싱 사용 (bcrypt, argon2 등)
  - 탐지 조건: password 필드 + DB 저장 로직 존재 시 검사
  - Grep: `(bcrypt|argon2|pbkdf2|hashlib)` 존재 확인
  - 해싱 라이브러리 미감지 시: [FAIL] + "password 해싱 미적용 — 프로덕션 배포 전 bcrypt/argon2 도입 필수"
- [ ] [해당 시][LOW] DB 연결 SSL 설정 확인
  - 탐지 조건: production 환경 설정 존재 시 검사
  - config.py에서 `sslmode` 확인

## 4. 입력 검증 (Input Validation)
Request DTO 및 router 파일에서 검사:

### Pydantic 검증
- [ ] [해당 시][MEDIUM] 이메일 필드에 `EmailStr` 타입 사용
  - 탐지 조건: `email` 필드가 Request/DTO에 존재 시만 검사
  - Grep: `email:\s*str` → `EmailStr` 권장
- [ ] [항상][MEDIUM] 문자열 필드에 길이 제한 존재
  - Grep: `:\s*str\s*$` (제한 없는 str 필드)
- [ ] [항상][LOW] 숫자 필드에 범위 제한 존재
  - Grep: `:\s*int\s*$` → `Field(ge=0)` 권장

### 파일 업로드
- [ ] [해당 시][HIGH] 파일 업로드 시 크기 제한 설정
  - 탐지 조건: **project-dna.md §8** "File Upload (UploadFile)" 상태 확인 → "미구현"이면 [SKIP]
  - Grep: `UploadFile` 사용 시 크기 검증 로직 확인
- [ ] [해당 시][HIGH] 파일 확장자/MIME 타입 검증
  - 탐지 조건: **project-dna.md §8** "File Upload (UploadFile)" 상태 확인 → "미구현"이면 [SKIP]
  - Grep: `content_type` 또는 `filename` 검증 확인

### Path Traversal
- [ ] [항상][CRITICAL] 사용자 입력을 파일 경로에 직접 사용하지 않음
  - Grep: `open\(.*\+|Path\(.*\+|os\.path\.join\(.*request`

## 5. 의존성/설정 (Dependency & Configuration)
설정 파일 및 pyproject.toml에서 검사:

### 취약 의존성
- [ ] [항상][HIGH] `pip audit` 또는 `uv pip audit` 실행 결과 취약점 없음
  - 실행: `uv pip audit 2>/dev/null || pip audit 2>/dev/null || echo "audit tool 미설치"`

### 디버그 모드
- [ ] [항상][CRITICAL] Production에서 debug=True 비활성화
  - Grep: `debug\s*=\s*True` (조건문 없이 직접 설정된 경우)
- [ ] [항상][HIGH] Production에서 docs/swagger 비활성화
  - config.py의 `docs_url`이 `is_dev` 조건 사용 확인

### CORS 설정
- [ ] [항상][HIGH] Production에서 `allow_origins=["*"]` 미사용
  - config.py의 `allow_origins`이 `is_dev` 조건으로 분기 확인
- [ ] [항상][MEDIUM] `allow_methods=["*"]`, `allow_headers=["*"]` 범위 검토

### 시크릿 관리
- [ ] [항상][CRITICAL] `.env` 파일이 `.gitignore`에 포함
  - .gitignore에서 `\.env` 패턴 존재 확인
- [ ] [항상][HIGH] 설정 값이 환경변수에서 로딩 (하드코딩 아님)
  - Settings 클래스에서 `validation_alias` 사용 확인
- [ ] [항상][MEDIUM] Field default 값에 실제 시크릿 미포함
  - Grep: `Field(default=` → default에 실제 credential 여부 확인

## 6. 에러 처리/로깅 (Error Handling & Logging)
미들웨어 및 예외 처리 파일에서 검사:

### 스택 트레이스 노출
- [ ] [항상][CRITICAL] Production에서 traceback 미노출
  - ExceptionMiddleware에서 `is_dev` 조건 확인
- [ ] [항상][HIGH] 에러 응답에 내부 구현 세부사항 미노출
  - Grep: `traceback|stack_trace|__traceback__` 반환 여부

### 에러 메시지 민감정보
- [ ] [항상][HIGH] 에러 메시지에 DB 쿼리/스키마 정보 미포함
  - Grep: `(table|column|schema|query).*Exception`
- [ ] [항상][MEDIUM] 데이터 ID 열거 공격 가능성 검토
  - Grep: `Data with ID` → 존재 시 인지 필요

### Rate Limiting
- [ ] [해당 시][MEDIUM] Rate limiting 미들웨어 설정 여부
  - 탐지 조건: **project-dna.md §8** "Rate Limiting (slowapi)" 상태 확인 → "미구현"이면 [SKIP]
  - Grep: `RateLimitMiddleware|slowapi|throttle|rate_limit`
  - 미설정 시: [SKIP] + "엔드포인트 확장 시 slowapi 도입 권장"

### 요청 크기 제한
- [ ] [해당 시][MEDIUM] 요청 본문 크기 제한 설정 여부
  - 탐지 조건: **project-dna.md §8** "File Upload (UploadFile)" 상태 확인 → "미구현"이면 [SKIP]
  - Grep: `max_content_length|body_limit|RequestSizeLimitMiddleware`
