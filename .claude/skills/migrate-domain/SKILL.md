---
name: migrate-domain
argument-hint: "generate|upgrade|downgrade|status"
disable-model-invocation: true
description: |
  This skill should be used when the user asks to "마이그레이션 생성",
  "migration 만들어줘", "migrate domain", "DB 마이그레이션", "alembic revision",
  "스키마 변경", "테이블 추가", "컬럼 추가", "DB 변경",
  or wants to create, apply, or rollback database migrations.
---

# Alembic 마이그레이션 관리

대상: $ARGUMENTS (generate | upgrade | downgrade | status)

## 사전 확인
1. `alembic.ini` 존재 확인
2. `_env/local.env` 파일 존재 및 DB 접속 정보 확인
3. 대상 도메인의 Model 파일 존재 확인: `src/{name}/infrastructure/database/models/{name}_model.py`

> **참고**: `migrations/env_utils.py`의 `load_models()`가 `src/*/infrastructure/database/models/` 하위
> 모든 모델을 **자동 탐지**한다. 별도 import 설정 불필요.

## 명령어 매핑

### generate (새 마이그레이션 생성)
```bash
alembic revision --autogenerate -m "{domain}: {description}"
```
- 메시지 형식: `"{domain}: {description}"` (예: `"user: add email_verified column"`)
- 생성된 파일을 반드시 사용자에게 보여주고 검토 요청

### upgrade (마이그레이션 적용)
```bash
alembic upgrade head    # 최신까지 적용
alembic upgrade +1      # 1단계만 적용
```

### downgrade (마이그레이션 롤백)
```bash
alembic downgrade -1    # 1단계 롤백
```

### status (현재 상태 확인)
```bash
alembic current         # 현재 적용된 revision
alembic history         # 전체 히스토리
```

## 워크플로우

### 새 도메인 추가 후 마이그레이션
1. `/new-domain {name}`으로 도메인 스캐폴딩 완료 확인
2. Model 파일 검토: `src/{name}/infrastructure/database/models/{name}_model.py`
3. `alembic revision --autogenerate -m "{name}: initial migration"`
4. 생성된 파일 검토: `migrations/versions/` 하위 최신 파일
5. 사용자에게 upgrade/downgrade 함수 확인 요청
6. 승인 후 `alembic upgrade head`로 적용

### 기존 도메인 모델 변경 후 마이그레이션
1. Model 변경 사항 확인 (Serena `find_symbol`로 변경 전/후 비교)
2. `alembic revision --autogenerate -m "{name}: {변경 설명}"`
3. 생성된 파일 검토
4. 사용자 승인 후 `alembic upgrade head`

## 주의사항
- **autogenerate는 100% 정확하지 않음** — 생성된 파일을 반드시 검토
- **column rename은 감지 불가** (drop+add로 생성됨) — 수동 수정 필요
- `alembic.ini`의 `env` 값이 환경에 맞는지 확인 (local/dev/stg/prod)
- **프로덕션 적용 시 반드시 백업 후 진행**
- `migrations/versions/` 디렉토리가 없으면 첫 revision 시 자동 생성됨

## upgrade/downgrade 후 검증
1. `alembic current` — 적용된 revision 확인
2. 도메인 통합 테스트 실행: `pytest tests/integration/{name}/ -v` (DB 스키마 일치 확인)
3. 사용자에게 결과 보고
