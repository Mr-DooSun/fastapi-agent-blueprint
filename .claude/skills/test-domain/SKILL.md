---
name: test-domain
argument-hint: "domain_name generate|run"
description: |
  This skill should be used when the user asks to "테스트 생성",
  "테스트 실행", "generate tests", "run tests for domain",
  "테스트 만들어줘", "unit test", "integration test", "pytest 실행",
  "테스트 코드 작성", or wants to create or run tests for a specific domain.
---

# 도메인 테스트 생성/실행

대상: $ARGUMENTS (도메인명 + "generate" 또는 "run")

인자가 "generate"를 포함하면 누락된 테스트 파일을 생성한다.
인자가 "run"을 포함하면 기존 테스트를 실행한다.
둘 다 없으면 사용자에게 어떤 모드인지 질문한다.

## 필수 테스트 파일 (4개)
- `tests/factories/{name}_factory.py`
- `tests/unit/{name}/domain/test_{name}_service.py`
- `tests/unit/{name}/application/test_{name}_use_case.py`
- `tests/integration/{name}/infrastructure/test_{name}_repository.py`

상세 테스트 패턴과 Factory 코드 예시는 `${CLAUDE_SKILL_DIR}/references/test-patterns.md`를 참조한다.

## Generate 모드 절차
1. `src/{name}/` 읽어서 모든 Service/UseCase 메서드 파악
2. `tests/` 디렉토리에서 기존 테스트 파일 확인
3. 누락된 파일 생성 (위 4개 + 필요한 `__init__.py`)

## Run 모드 절차
```bash
# 단위 테스트
pytest tests/unit/{name}/ -v

# 통합 테스트
pytest tests/integration/{name}/ -v

# 전체
pytest tests/unit/{name}/ tests/integration/{name}/ tests/e2e/{name}/ -v
```

실패한 테스트가 있으면 원인을 분석하고 수정 방안을 제시한다.

## Generate 후 검증
1. 생성된 테스트 파일 import 확인: `python -c "from tests.unit.{name}.domain.test_{name}_service import *; print('OK')"`
2. 테스트 실행: `pytest tests/unit/{name}/ tests/integration/{name}/ -v`
3. pre-commit 실행: `pre-commit run --files tests/**/{name}/**/*.py`
