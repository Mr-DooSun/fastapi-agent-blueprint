# 🤝 기여 가이드 (Contributing Guide)

FastAPI Layered Architecture 프로젝트에 기여해 주셔서 감사합니다! 

이 문서는 프로젝트에 기여하는 방법을 안내합니다.

---

## 📋 목차

- [행동 강령](#-행동-강령)
- [기여 방법](#-기여-방법)
- [개발 환경 설정](#-개발-환경-설정)
- [코딩 규칙](#-코딩-규칙)
- [Commit 메시지 규칙](#-commit-메시지-규칙)
- [Pull Request 프로세스](#-pull-request-프로세스)
- [이슈 작성 가이드](#-이슈-작성-가이드)

---

## 📜 행동 강령

### 우리의 약속

우리는 개방적이고 환영하는 환경을 조성하기 위해 다음을 약속합니다:

- 모든 기여자를 존중합니다
- 건설적인 피드백을 제공합니다
- 다양한 관점과 경험을 환영합니다
- 커뮤니티의 이익을 최우선으로 합니다

### 금지 사항

- 차별적이거나 모욕적인 언어 사용
- 개인 공격 또는 정치적 공격
- 괴롭힘 (공개적이든 사적이든)
- 타인의 개인 정보 공개

---

## 🎯 기여 방법

다음과 같은 방법으로 기여할 수 있습니다:

### 1️⃣ 버그 리포트

버그를 발견하셨나요? [Issues](../../issues)에 다음 정보를 포함하여 보고해 주세요:

- **명확한 제목**: 버그를 한 줄로 설명
- **재현 단계**: 버그를 재현하는 방법
- **예상 동작**: 어떻게 동작해야 하는지
- **실제 동작**: 실제로 어떻게 동작하는지
- **환경 정보**: Python 버전, OS, 의존성 버전

### 2️⃣ 기능 제안

새로운 기능을 제안하시나요? [Issues](../../issues)에 다음을 포함하여 작성해 주세요:

- **명확한 제목**: 기능을 한 줄로 설명
- **문제 정의**: 어떤 문제를 해결하나요?
- **제안하는 해결책**: 어떻게 구현하면 좋을까요?
- **대안**: 고려한 다른 방법이 있나요?

### 3️⃣ 문서 개선

- 오타 수정
- 설명 추가 또는 개선
- 예제 코드 추가
- 다국어 번역

### 4️⃣ 코드 기여

- 버그 수정
- 기능 추가
- 성능 개선
- 리팩토링

---

## 🛠️ 개발 환경 설정

### 1️⃣ Fork 및 Clone

```bash
# 1. GitHub에서 Fork 버튼 클릭

# 2. Fork한 저장소 Clone
git clone https://github.com/YOUR_USERNAME/fastapi-layered-architecture.git
cd fastapi-layered-architecture

# 3. Upstream 저장소 추가
git remote add upstream https://github.com/ORIGINAL_OWNER/fastapi-layered-architecture.git
```

### 2️⃣ 가상환경 및 의존성 설치

```bash
# UV 사용 (권장)
uv venv --python 3.12.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 또는 pip 사용
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3️⃣ Pre-commit Hook 설정

```bash
pre-commit install
```

### 4️⃣ 환경변수 설정

```bash
cp _env/local.env.example _env/local.env
# _env/local.env 파일을 편집하여 로컬 환경에 맞게 수정
```

### 5️⃣ 데이터베이스 설정

```bash
# MySQL 컨테이너 실행
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=fastapi_db \
  -p 3306:3306 \
  mysql:8.0

# 마이그레이션 실행
alembic upgrade head
```

### 6️⃣ 서버 실행 확인

```bash
python run_server_local.py --env local
```

http://localhost:8000/api/docs 에 접속하여 정상 동작 확인

---

## 📏 코딩 규칙

### 코드 스타일

이 프로젝트는 **Ruff**를 사용하여 린팅과 포매팅을 통합 관리합니다:

#### Ruff (린팅 + 포매팅)

```bash
# 린트 체크 + 자동 수정
ruff check src/ --fix

# 코드 포매팅
ruff format src/
```

- 라인 길이: 88자
- Import 정렬: Black 호환 (자동)
- Python 3.12+ 구문 현대화 (자동)
- 미사용 import/변수 제거 (자동)
- 보안 검사 (flake8-bandit 호환)

### 타입 힌팅

모든 함수와 메서드에 타입 힌트를 추가하세요:

```python
# ✅ 좋은 예
async def create_user(entity: CreateUserEntity) -> UserEntity:
    ...

# ❌ 나쁜 예
async def create_user(entity):
    ...
```

### Docstring

복잡한 로직에는 Docstring을 추가하세요:

```python
def make_pagination(total_items: int, page: int, page_size: int) -> PaginationInfo:
    """
    페이지네이션 정보를 생성합니다.
    
    Args:
        total_items: 전체 아이템 수
        page: 현재 페이지 번호 (1부터 시작)
        page_size: 페이지당 아이템 수
        
    Returns:
        PaginationInfo: 페이지네이션 메타데이터
    """
    ...
```

### 네이밍 규칙

- **함수/메서드**: `snake_case`
  - 예: `create_user`, `get_data_by_id`
- **클래스**: `PascalCase`
  - 예: `UserService`, `BaseRepository`
- **상수**: `UPPER_SNAKE_CASE`
  - 예: `MAX_PAGE_SIZE`, `API_VERSION`
- **Private 메서드**: `_underscore_prefix`
  - 예: `_get_headers`, `_validate_entity`

---

## 📝 Commit 메시지 규칙

### Commit 메시지 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 포맷팅 (기능 변경 없음)
- **refactor**: 리팩토링
- **test**: 테스트 추가
- **chore**: 빌드/도구 변경
- **perf**: 성능 개선

### Scope (선택)

변경 범위를 명시:
- `user`: User 도메인
- `core`: Core 인프라
- `di`: 의존성 주입
- `db`: 데이터베이스

### Subject

- 50자 이내
- 명령형으로 작성 ("추가한다" ❌, "추가" ✅)
- 마침표 없음

### 예시

```
feat(user): 이메일 중복 체크 기능 추가

사용자 등록 시 이메일 중복을 체크하는 로직을 추가했습니다.
- UserRepository에 find_by_email 메서드 추가
- UserService에서 이메일 중복 시 예외 발생

Closes #123
```

```
fix(db): 연결 풀 설정 오류 수정

pool_size가 올바르게 적용되지 않는 문제를 수정했습니다.

Fixes #456
```

---

## 🔄 Pull Request 프로세스

### 1️⃣ 브랜치 생성

```bash
# 최신 코드 가져오기
git fetch upstream
git checkout main
git merge upstream/main

# 새 브랜치 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/your-bug-fix
```

### 2️⃣ 코드 작성

- 작은 단위로 자주 커밋
- 커밋 메시지 규칙 준수
- Pre-commit Hook 통과 확인

```bash
# Pre-commit 수동 실행
pre-commit run --all-files
```

### 3️⃣ 테스트

```bash
# 서버 실행 테스트
python run_server_local.py --env local

# API 문서 확인
# http://localhost:8000/api/docs
```

### 4️⃣ Push

```bash
git push origin feature/your-feature-name
```

### 5️⃣ Pull Request 생성

GitHub에서 Pull Request를 생성하고 다음을 포함하세요:

**PR 제목**:
```
feat(user): 이메일 중복 체크 기능 추가
```

**PR 설명**:
```markdown
## 변경 사항
- UserRepository에 find_by_email 메서드 추가
- UserService에서 이메일 중복 시 예외 발생

## 관련 이슈
Closes #123

## 테스트 방법
1. 사용자 생성 API 호출 (POST /api/v1/user)
2. 같은 이메일로 다시 호출
3. 400 에러가 반환되는지 확인

## 체크리스트
- [x] 코드가 프로젝트 코딩 규칙을 준수함
- [x] 변경 사항에 대한 테스트를 수행함
- [x] 문서가 업데이트됨 (필요한 경우)
- [x] Pre-commit hook이 통과함
```

### 6️⃣ 리뷰 대응

- 리뷰어의 피드백에 신속하게 응답
- 수정이 필요한 경우 같은 브랜치에 추가 커밋
- 리뷰가 완료되면 메인테이너가 병합

---

## 📋 이슈 작성 가이드

### 버그 리포트 템플릿

```markdown
## 버그 설명
명확하고 간결하게 버그를 설명하세요.

## 재현 단계
1. '...'로 이동
2. '....'를 클릭
3. '....'까지 스크롤
4. 에러 발생

## 예상 동작
어떻게 동작해야 하는지 설명하세요.

## 실제 동작
실제로 어떻게 동작하는지 설명하세요.

## 스크린샷
가능하면 스크린샷을 첨부하세요.

## 환경
- OS: [예: Ubuntu 22.04]
- Python 버전: [예: 3.12.9]
- FastAPI 버전: [예: 0.115.0]

## 추가 정보
다른 컨텍스트를 추가하세요.
```

### 기능 제안 템플릿

```markdown
## 해결하려는 문제
현재 어떤 문제가 있나요?

## 제안하는 해결책
어떤 기능을 추가하면 좋을까요?

## 대안
고려한 다른 방법이 있나요?

## 추가 정보
다른 컨텍스트나 스크린샷을 추가하세요.
```

---

## 🧪 테스트 가이드

### 수동 테스트

```bash
# 1. 서버 실행
python run_server_local.py --env local

# 2. API 문서 확인
# http://localhost:8000/api/docs

# 3. API 테스트
curl -X POST "http://localhost:8000/api/v1/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 단위 테스트 (향후 추가 예정)

```python
# tests/test_user_service.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_user():
    # Given
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.insert_data.return_value = UserEntity(...)
    service = UserService(user_repository=mock_repo)
    
    # When
    result = await service.create_data(CreateUserEntity(...))
    
    # Then
    assert result.id == 1
    mock_repo.insert_data.assert_called_once()
```

---

## 📚 참고 자료

### 프로젝트 관련

- [README.md](README.md) - 프로젝트 개요 및 사용법
- [LICENSE](LICENSE) - MIT 라이선스

### 외부 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🎁 기여자 감사

모든 기여자에게 감사드립니다! 

기여자 목록은 [Contributors](../../graphs/contributors) 페이지에서 확인할 수 있습니다.

---

## 📞 질문이 있으신가요?

- **Issues**: 버그 리포트 및 기능 제안
- **Discussions**: 아키텍처 관련 질문 및 토론

---

**다시 한번 기여해 주셔서 감사합니다! 🙏**

