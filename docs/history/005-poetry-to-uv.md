# 005. Poetry에서 uv로 전환

- 상태: Accepted
- 날짜: 2025-04-16
- 관련 이슈: #3
- 관련 PR: #4
- 관련 커밋: `de6e063`

## 배경

프로젝트의 Python 버전 관리와 패키지 관리를 각각 다른 도구로 수행하고 있었다.

- **Python 버전 관리**: pyenv
- **패키지 관리**: Poetry

두 도구를 별도로 설치·설정·유지해야 했고,
새 팀원이 환경을 구축할 때 pyenv와 Poetry를 각각 설치하고 연동하는 과정이 필요했다.

## 문제

### 1. 도구 분산

pyenv로 Python 버전을 설치하고, Poetry로 가상환경과 의존성을 관리하는 이원 체제였다.
두 도구의 설정이 서로 독립적이어서, Python 버전 변경 시 Poetry 가상환경을 재생성하는 등
연동 작업이 필요했다.

### 2. 속도

Poetry의 의존성 해석(resolution)과 lock 파일 생성이 느렸다.
특히 의존성이 늘어날수록 `poetry lock` 실행 시간이 체감될 정도로 길어졌다.

## 검토한 대안

### 1. Poetry 유지
- 장점: 이미 익숙하고, 생태계가 성숙함
- 단점: pyenv 의존 유지, 느린 의존성 해석

### 2. uv
- Rust 기반으로 의존성 해석 속도가 Poetry 대비 10~100배 빠름
- Python 버전 관리(`uv python install`)와 패키지 관리를 하나의 도구로 통합
- `pyproject.toml` PEP 표준 형식 사용 (Poetry 전용 `[tool.poetry]` 섹션 불필요)

## 결정

**uv 채택**

```toml
# Before (Poetry) — pyproject.toml
[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[project]
dependencies = [
    "fastapi (>=0.115.8,<0.116.0)",  # Poetry 전용 버전 표기
    ...
]
```

```toml
# After (uv) — pyproject.toml
[project]
requires-python = ">=3.12.8"
dependencies = [
    "fastapi>=0.115.12",  # PEP 508 표준 표기
    ...
]
# build-system 섹션 제거
```

- `poetry.lock` (1,248줄) → `uv.lock` (685줄)으로 lock 파일 크기도 약 45% 감소

## 근거

| 기준 | Poetry + pyenv | uv |
|------|---------------|-----|
| Python 버전 관리 | pyenv 별도 필요 | `uv python install`로 통합 |
| 의존성 해석 속도 | 느림 | Rust 기반, 10~100배 빠름 |
| 도구 설치 | pyenv + Poetry 2개 | uv 1개 |
| pyproject.toml 형식 | Poetry 전용 문법 포함 | PEP 표준 준수 |
| lock 파일 크기 | 1,248줄 | 685줄 |

1. Python 버전과 패키지를 하나의 도구로 관리할 수 있어 환경 구축이 단순해짐
2. 의존성 해석 속도가 체감될 정도로 빨라져 개발 경험이 개선됨
3. PEP 표준 `pyproject.toml` 형식을 사용하여 도구 종속성이 줄어듦
