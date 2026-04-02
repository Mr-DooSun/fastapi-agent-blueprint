# Architecture Conventions

> For Absolute Prohibitions (including CLAUDE.md modification rules), Conversion Patterns, and Write DTO criteria, refer to CLAUDE.md.
> This memory only contains **structural context** not covered in CLAUDE.md.

## Data Flow (3-Tier Hybrid)
```
Default (simple CRUD):
  Write: Request → Service(BaseService) → Repository → Model → DB
  Read:  Response ← Service ← Repository ← DTO ← Model

Complex logic:
  Write: Request → UseCase → Service → Repository → Model → DB
  Read:  Response ← UseCase ← Service ← Repository ← DTO ← Model
```
> UseCase is added only when combining multiple Services, crossing transaction boundaries, or publishing events
> For detailed Conversion Patterns: refer to the "Conversion Patterns" section in CLAUDE.md

## Object Roles

### DTO (Domain DTO)
- Location: `src/{domain}/domain/dtos/{domain}_dto.py`
- Role: Carries read results from Repository → Service → Router (full data)
- **Read-only, single type**: `{Name}DTO` — may include sensitive fields (password, etc.)
- Create/Update DTO is only created separately when fields differ from Request

### API Schema (Interface DTO)
- Location: `src/{domain}/interface/server/schemas/{domain}_schema.py`
- Inherits `BaseRequest` / `BaseResponse`
- Explicit field declarations
- Intentionally excludes sensitive fields (Response)
- When fields are identical, Request also serves as the layer DTO

### Model (SQLAlchemy ORM)
- Location: `src/{domain}/infrastructure/database/models/{domain}_model.py`
- Must never leave the Repository layer
- Conversion: `DTO → Model: Model(**dto.model_dump())`
- Conversion: `Model → DTO: DTO.model_validate(model, from_attributes=True)`
