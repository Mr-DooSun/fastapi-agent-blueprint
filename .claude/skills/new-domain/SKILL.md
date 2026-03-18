---
name: new-domain
argument-hint: domain_name
description: |
  This skill should be used when the user asks to "새 도메인 추가",
  "create a new domain", "도메인 스캐폴딩", "도메인 만들어줘",
  or mentions adding a new bounded context to the project.
---

# 새 도메인 스캐폴딩

도메인명: $ARGUMENTS

## 현재 존재하는 도메인
!`ls -d src/*/ 2>/dev/null | grep -v _core | grep -v _apps | sed 's|src/||;s|/||' || echo "(none)"`

## 사전 확인
1. `$ARGUMENTS`가 유효한 Python 식별자인지 확인 (소문자, 언더스코어 허용, 하이픈 금지)
2. `src/$ARGUMENTS/` 디렉토리가 이미 존재하는지 확인 — 존재하면 중단
3. Serena `architecture_conventions` 메모리 읽기 — 객체 역할 및 데이터 흐름 확인
4. 사용자에게 도메인의 **주요 필드**를 질문 (예: name, description, price 등)

## 스캐폴딩 절차

`src/user/`를 레퍼런스로 삼아 6개 Layer를 순서대로 생성한다.
각 파일 생성 전에 해당 user 파일을 읽고 패턴을 복제한다.

상세 파일 목록과 import 경로는 `${CLAUDE_SKILL_DIR}/references/scaffolding-layers.md`를 참조한다.

**Layer 순서**: Domain → Application → Infrastructure → Interface → 앱 와이어링 → 테스트

총 26개 파일 생성 (빈 `__init__.py` 포함).

## 아키텍처 규칙
CLAUDE.md의 "절대 금지 규칙" 및 "변환 패턴"을 준수한다.

## 완료 후 검증
1. `python -c "from src.{name}.domain.dtos.{name}_dto import {Name}DTO; print('OK')"` — import 확인
2. pre-commit 실행: `pre-commit run --files src/{name}/**/*.py`
3. 테스트 실행: `pytest tests/unit/{name}/ -v`
4. 사용자에게 결과 보고
