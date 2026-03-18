# Architecture Conventions

> 절대 금지 규칙, 변환 패턴, Write DTO 기준은 CLAUDE.md를 참조.
> 이 메모리는 CLAUDE.md에 없는 **구조적 컨텍스트**만 담는다.

## 데이터 흐름
```
Request → UseCase → Service → Repository → Model
                                         ↓
                              DTO.model_validate(model, from_attributes=True)
                                         ↓
                              Response(**dto.model_dump(exclude={...}))
```
> 변환 패턴 상세: CLAUDE.md "변환 패턴" 섹션 참조

## 객체 역할

### DTO (Domain DTO)
- 위치: `src/{domain}/domain/dtos/{domain}_dto.py`
- 역할: Repository → Service → UseCase 읽기 결과 전달 (full data)
- **읽기 전용 1종**: `{Name}DTO` — 민감 필드(password 등) 포함 가능
- Create/Update DTO는 Request 필드와 다를 때만 별도 생성

### API Schema (Interface DTO)
- 위치: `src/{domain}/interface/server/dtos/{domain}_dto.py`
- `BaseRequest` / `BaseResponse` 상속
- 명시적 필드 선언 (다중상속 금지)
- 민감 필드 의도적 제외 (Response)
- Request는 필드가 동일한 경우 레이어 DTO 역할도 겸함

### Model (SQLAlchemy ORM)
- 위치: `src/{domain}/infrastructure/database/models/{domain}_model.py`
- Repository 레이어 밖으로 절대 나가지 않음
- 변환: `DTO → Model: Model(**dto.model_dump())`
- 변환: `Model → DTO: DTO.model_validate(model, from_attributes=True)`
