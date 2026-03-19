# 010. 코드 품질 도구 체계화

- 상태: Accepted
- 날짜: 2025-10-15
- 관련 이슈: #34, #41
- 관련 PR: #42
- 관련 커밋: `186c0f1`, `2463f02`

## 배경

프로젝트 초기에는 기본적인 pre-commit 설정만 있었다.
팀 규모가 커지고 코드량이 늘어나면서,
코드 컨벤션을 타이트하게 잡아 일관성을 유지하고 싶었다.

## 문제

### 1. 느슨한 코드 컨벤션

기존 pre-commit 설정이 최소한이어서,
PR 리뷰에서 스타일 관련 논의에 시간이 소모될 수 있는 구조였다.
자동화로 처리할 수 있는 부분은 도구에 맡기고 싶었다.

### 2. 불필요한 관행 유지

Python 3.x 환경에서 불필요한 `# -*- coding: utf-8 -*-` 헤더가 모든 파일에 포함되어 있었다.
Python 3은 기본 인코딩이 UTF-8이므로 이 헤더는 의미가 없다.

## 결정

### pre-commit 설정 확대 개편

`.pre-commit-config.yaml`을 대폭 강화했다 (커밋 `186c0f1`).

주요 변경:
- **기존 UTF-8 인코딩 헤더 일괄 제거**: 40개 파일에서 `# -*- coding: utf-8 -*-` 제거
- **포맷팅 도구 강화**: trailing whitespace, end-of-file fixer, mixed line ending 등
- **정적 분석 추가**: import 정렬, 타입 체크 등

### mypy 수동 모드 도입

mypy를 pre-commit에 등록하되, `--hook-stage manual`로 설정했다.

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  hooks:
    - id: mypy
      # 수동 실행: pre-commit run --hook-stage manual mypy
```

- 매 커밋마다 자동 실행하면 느려서 개발 흐름이 끊김
- 필요할 때 수동으로 `pre-commit run --hook-stage manual mypy` 실행
- CI에서는 자동 실행 가능

## 근거

| 기준 | 최소 pre-commit | 강화된 pre-commit |
|------|----------------|-------------------|
| 스타일 논의 | PR 리뷰에서 수동 | 자동 포맷팅으로 제거 |
| 코드 일관성 | 개인 스타일 의존 | 도구로 강제 |
| 불필요 코드 | UTF-8 헤더 유지 | 일괄 제거 |
| 타입 체크 | 없음 | mypy (수동 모드) |

1. 코드 컨벤션은 최대한 도구로 자동화하여, 리뷰에서 로직에 집중할 수 있게 함
2. Python 3 기본 UTF-8이므로 인코딩 헤더는 불필요한 boilerplate
3. mypy는 수동 모드로 도입하여 개발 속도와 타입 안전성을 균형있게 확보
