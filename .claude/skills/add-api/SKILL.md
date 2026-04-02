---
name: add-api
argument-hint: "Add METHOD /path to a domain"
description: |
  This skill should be used when the user asks to
  "add endpoint", "add route", "add API",
  or wants to add a new route to an existing domain.
---

# Add API Endpoint

Request: $ARGUMENTS

## Analysis

1. Identify from the request: domain name, HTTP method, path, purpose
2. Use Serena `find_symbol` to explore the domain's existing Router, Service, Repository (also check UseCase if present)
3. Determine what is needed:
   - Is a new Request/Response DTO required? (Or are existing ones sufficient?)
   - Is a new Service method required? (Or are BaseService methods sufficient?)
   - Is a new Repository method required? (Is a custom query needed?)
   - Is a UseCase required? (Only when complex logic such as combining multiple Services is involved)

## Implementation Order (Bottom-up)

### 1. Repository (only when a custom query is needed)
- Add method signature to Protocol: `src/{name}/domain/protocols/{name}_repository_protocol.py`
- Add implementation to Repository: `src/{name}/infrastructure/repositories/{name}_repository.py`
- Skip this step if BaseRepository methods are sufficient

### 2. Service
- Add method to `src/{name}/domain/services/{name}_service.py`
- BaseService provides basic CRUD + pagination, so only add methods when custom logic is needed

### 3. UseCase (only when complex logic is needed)
- Only add `src/{name}/application/use_cases/{name}_use_case.py` when a complex workflow such as combining multiple Services is required
- Simple CRUD is sufficient with direct Router → Service injection

### 4. Interface DTO (if needed)
- Add Request/Response to `src/{name}/interface/server/schemas/{name}_schema.py`
- Request inherits from `BaseRequest`, Response inherits from `BaseResponse`
- **Explicit field declaration** (single inheritance from BaseRequest/BaseResponse only)

### 5. Router
- Add endpoint to `src/{name}/interface/server/routers/{name}_router.py`
- Router pattern: see **project-dna.md §9**
- Conversion Patterns: see **project-dna.md §6**

## Conversion Rules
For Conversion Patterns see **project-dna.md §6**. For import paths see **project-dna.md §2**.

## Post-completion Verification
1. Run pre-commit
2. Add tests for the new method to the domain's unit tests
3. Inform that the endpoint can be verified in Swagger after starting the server
