# 아키텍처 감사 체크리스트 상세

> 기대 패턴의 상세 정의는 `.claude/skills/_shared/project-dna.md`를 참조한다.

## 1. 레이어 의존성 규칙
각 도메인의 Python 파일에 대해 Grep으로 검사:

- [ ] `src/{name}/domain/` 파일에서 `from src.{name}.infrastructure` import 없음
- [ ] `src/{name}/domain/` 파일에서 `from src.{name}.interface` import 없음
- [ ] `src/{name}/application/` 파일에서 `from src.{name}.infrastructure` import 없음 (DI 제외)
- [ ] `src/{name}/domain/` 파일에서 `from sqlalchemy` import 없음
- [ ] `src/{name}/domain/` 파일에서 `from dependency_injector` import 없음

## 2. 변환 패턴 준수
전체 도메인 파일에서 검사:

- [ ] `to_entity(` 메서드 호출 없음
- [ ] `from_entity(` 메서드 호출 없음
- [ ] `class.*Mapper` 클래스 정의 없음
- [ ] Repository 메서드 반환값이 DTO 타입 (Model 객체 노출 없음)
- [ ] Model → DTO 변환이 `model_validate(..., from_attributes=True)` 사용

## 3. DTO/Response 무결성
interface/server/dtos/ 파일에서 검사:

- [ ] Response 클래스가 `BaseResponse`만 상속 (다중상속 없음)
- [ ] Request 클래스가 `BaseRequest`만 상속 (다중상속 없음)
- [ ] 민감 필드(password 등)가 Response에 포함되지 않음
- [ ] Router에서 `model_dump(exclude={...})`로 민감 필드 제외

## 4. DI Container 정확성
infrastructure/di/ 파일에서 검사 (기대 패턴: **project-dna.md §5** 참조):

- [ ] Container가 `containers.DeclarativeContainer` 상속
- [ ] `core_container = providers.DependenciesContainer()` 선언
- [ ] Repository가 `providers.Singleton` 사용
- [ ] Service가 `providers.Factory` 사용
- [ ] UseCase가 `providers.Factory` 사용

## 5. 테스트 커버리지
tests/ 디렉토리에서 검사:

- [ ] `tests/factories/{name}_factory.py` 존재
- [ ] `tests/unit/{name}/domain/test_{name}_service.py` 존재
- [ ] `tests/unit/{name}/application/test_{name}_use_case.py` 존재
- [ ] `tests/integration/{name}/infrastructure/test_{name}_repository.py` 존재

## 6. Bootstrap 와이어링
앱 레벨 파일 및 자동 발견 메커니즘 검사:

- [ ] `src/{name}/interface/server/bootstrap/{name}_bootstrap.py` 존재
- [ ] `src/{name}/infrastructure/di/{name}_container.py` 존재 (자동 발견 조건)
- [ ] `src/{name}/__init__.py` 존재 (자동 발견 조건)
- [ ] `wire(packages=[...])` 호출이 올바른 패키지를 대상으로 함
- [ ] **참고**: `discover_domains()`가 자동 탐지하므로 App-level `container.py`/`bootstrap.py` 수동 등록 불필요 (project-dna.md §5)
