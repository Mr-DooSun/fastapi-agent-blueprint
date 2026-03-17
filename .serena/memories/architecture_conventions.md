# Architecture Conventions

## Data Flow
```
Request(BaseRequest)
→ UseCase → Service → Repository  (필드 동일 시 item 직접 전달)
→ DTO.model_validate(model, from_attributes=True)
→ Response(**dto.model_dump(exclude={'password'}))
```

### Write DTO 생성 기준
- Request 필드 == Domain 필드: Request 직접 전달 (변환 없음)
- Request 필드 != Domain 필드 (auth context, 파생값 등): 별도 DTO 생성 후 변환

## Object Roles

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
- Request는 필드가 동일한 경우 레이어 DTO 역할도 겸함 (별도 Create/UpdateDTO 불필요)

### Model (SQLAlchemy ORM)
- 위치: `src/{domain}/infrastructure/database/models/{domain}_model.py`
- Repository 레이어 밖으로 절대 나가지 않음
- 변환: `DTO → Model: Model(**dto.model_dump())`
- 변환: `Model → DTO: DTO.model_validate(model, from_attributes=True)`

## DO ✅
- DTO를 모든 레이어에서 직접 사용
- Protocol을 DIP 도구로 사용 (Domain이 Infrastructure import 안 하도록)
- 인라인 변환 (`model_dump`, `model_validate`)

## DON'T ❌
- `class UserResponse(BaseResponse, UserEntity)` 같은 다중상속
- `to_entity()`, `from_entity()` 메서드 사용
- Domain 레이어에서 Infrastructure import
- Model 객체를 Repository 밖으로 노출
- Mapper 클래스 별도 생성
