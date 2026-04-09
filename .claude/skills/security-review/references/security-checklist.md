# Security Audit Checklist Details

> **Classification**: `[Always]` = always check | `[When applicable]` = check only when the feature is in use (output [SKIP] when not in use)
>
> **Automatic conditional check determination**: Whether `[When applicable]` items are active is
> pre-determined using the "Active Features" table in `.claude/skills/_shared/project-dna.md` section 8.
> `[When applicable]` items for features marked "not implemented" in section 8 are immediately [SKIP]ped without Grep.

## 1. Injection Prevention

Grep-check each target Python file:

### SQL Injection
- [ ] [Always][CRITICAL] No `f"SELECT ` / `f"INSERT ` / `f"UPDATE ` / `f"DELETE ` patterns
  - Grep: `f["'].*\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b`
- [ ] [Always][CRITICAL] No `.format()` + SQL keyword combinations
  - Grep: `\.format\(.*\).*(SELECT|INSERT|UPDATE|DELETE)`
- [ ] [Always][HIGH] When using `text()`, parameter binding applied (no f-string + text() combination)
  - Grep: `text\(f["']`
- [ ] [Always][MEDIUM] No `exec()` / `eval()` usage
  - Grep: `\bexec\s*\(|\beval\s*\(`

### Command Injection
- [ ] [Always][CRITICAL] No `subprocess.*(shell=True)` usage
  - Grep: `subprocess\.\w+\(.*shell\s*=\s*True`
- [ ] [Always][CRITICAL] No `os.system(` usage
  - Grep: `os\.system\s*\(`
- [ ] [Always][HIGH] No `os.popen(` usage
  - Grep: `os\.popen\s*\(`

### Template Injection
- [ ] [When applicable][MEDIUM] When using Jinja2, `autoescape=True` is set
  - Detection condition: Check when `from jinja2` or `Environment(` import exists (not registered in project-dna.md section 8 — verify directly via Grep)
  - Grep: `Environment\(` -> verify autoescape setting

## 2. Authentication & Authorization

Check router files and configuration files:

### Endpoint Protection
- [ ] [Always][CRITICAL] POST/PUT/DELETE endpoints have authentication dependency
  - Grep: `@router\.(post|put|delete|patch)` -> verify `Depends(.*auth|.*current_user|.*token)` in the function
  - When not implemented: [FAIL] + "Authentication not implemented — must be implemented before production deployment" warning
### Admin Dashboard Security
- [ ] [Always][HIGH] Admin endpoint access restriction verified
  - Grep: Every `@ui.page("/admin/` function calls `require_auth()` before any rendering
- [ ] [Always][HIGH] Admin authentication uses timing-safe comparison
  - Grep: Verify `hmac.compare_digest` in `src/_core/infrastructure/admin/auth.py` (not `==` for password comparison)
- [ ] [Always][HIGH] Sensitive fields masked in admin grid
  - Grep: Fields containing `password`, `secret`, `token`, `key` in ColumnConfig use `masked=True`
- [ ] [Always][MEDIUM] Admin credentials managed via environment variables
  - Grep: `settings.admin_id` and `settings.admin_password` (not hardcoded in auth.py)
- [ ] [Always][MEDIUM] Admin session storage secret is non-default
  - Grep: `admin_storage_secret` loaded from environment settings (not hardcoded string)
- [ ] [Always][LOW] Admin pages do not directly import domain Services
  - Grep: No `from src.*.domain.services` in `interface/admin/pages/` files

### Credential Management
- [ ] [Always][CRITICAL] No hardcoded password/secret/api_key/token
  - Grep: `(password|secret|api_key|token)\s*=\s*["'][^"']{3,}["']`
  - Exclude: Field(), os.environ, settings., getenv, test files
- [ ] [When applicable][HIGH] JWT configuration verified
  - Detection condition: Check **project-dna.md section 8** "JWT/Authentication" status -> [SKIP] if "not implemented"
  - Grep: `algorithm.*=.*HS256` -> verify RS256 recommendation
  - Grep: `exp.*timedelta` -> verify expiration time appropriateness

### RBAC
- [ ] [When applicable][MEDIUM] Role-based access control verified
  - Detection condition: Check **project-dna.md section 8** "RBAC/Permissions" status -> [SKIP] if "not implemented"
  - Verify role check dependency usage in router

## 3. Data Protection

Check DTO, Response, and log files:

### PII Exposure Prevention
- [ ] [Always][CRITICAL] Response DTO does not contain password field
  - Grep: No password field in `class.*Response` block
  - Or: Verify `model_dump(exclude=.*password)` usage
- [ ] [Always][HIGH] Response DTO does not contain sensitive fields
  - Check targets: ssn, social_security, credit_card, card_number, secret, token, private_key
- [ ] [Always][HIGH] Logs do not contain PII
  - Grep: `(logger\.|logging\.|print\().*(password|secret|token|ssn|credit)`

### Encryption
- [ ] [When applicable][MEDIUM] Password hashing in use (bcrypt, argon2, etc.)
  - Detection condition: Check when password field + DB storage logic exist
  - Grep: Verify `(bcrypt|argon2|pbkdf2|hashlib)` presence
  - When hashing library not detected: [FAIL] + "Password hashing not applied — bcrypt/argon2 adoption required before production deployment"
- [ ] [When applicable][LOW] DB connection SSL configuration verified
  - Detection condition: Check when production environment settings exist
  - Verify `sslmode` in config.py

## 4. Input Validation

Check Request DTO and router files:

### Pydantic Validation
- [ ] [When applicable][MEDIUM] Email fields use `EmailStr` type
  - Detection condition: Check only when `email` field exists in Request/DTO
  - Grep: `email:\s*str` -> recommend `EmailStr`
- [ ] [Always][MEDIUM] String fields have length limits
  - Grep: `:\s*str\s*$` (str fields without limits)
- [ ] [Always][LOW] Numeric fields have range limits
  - Grep: `:\s*int\s*$` -> recommend `Field(ge=0)`

### File Upload
- [ ] [When applicable][HIGH] File upload size limit configured
  - Detection condition: Check **project-dna.md section 8** "File Upload (UploadFile)" status -> [SKIP] if "not implemented"
  - Grep: Verify size validation logic when `UploadFile` is used
- [ ] [When applicable][HIGH] File extension/MIME type validation
  - Detection condition: Check **project-dna.md section 8** "File Upload (UploadFile)" status -> [SKIP] if "not implemented"
  - Grep: Verify `content_type` or `filename` validation

### Path Traversal
- [ ] [Always][CRITICAL] User input not used directly in file paths
  - Grep: `open\(.*\+|Path\(.*\+|os\.path\.join\(.*request`

## 5. Dependencies & Configuration

Check configuration files and pyproject.toml:

### Vulnerable Dependencies
- [ ] [Always][HIGH] No vulnerabilities found in `pip audit` or `uv pip audit` results
  - Execute: `uv pip audit 2>/dev/null || pip audit 2>/dev/null || echo "audit tool not installed"`

### Debug Mode
- [ ] [Always][CRITICAL] debug=True disabled in production
  - Grep: `debug\s*=\s*True` (when set directly without conditional)
- [ ] [Always][HIGH] docs/swagger disabled in production
  - Verify `docs_url` in config.py uses `is_dev` condition

### CORS Configuration
- [ ] [Always][HIGH] `allow_origins=["*"]` not used in production
  - Verify `allow_origins` in Settings class or bootstrap uses environment-driven values (not hardcoded `["*"]`)
- [ ] [Always][MEDIUM] Review scope of `allow_methods=["*"]`, `allow_headers=["*"]`

### Secret Management
- [ ] [Always][CRITICAL] `.env` file included in `.gitignore`
  - Verify `\.env` pattern exists in .gitignore
- [ ] [Always][HIGH] Configuration values loaded from environment variables (not hardcoded)
  - Verify Settings class uses `validation_alias`
- [ ] [Always][MEDIUM] Field default values do not contain actual secrets
  - Grep: `Field(default=` -> verify whether default contains actual credentials

## 6. Error Handling & Logging

Check middleware and exception handling files:

### Stack Trace Exposure
- [ ] [Always][CRITICAL] Traceback not exposed in production
  - Verify `is_dev` condition in `generic_exception_handler` (exception_handlers.py)
- [ ] [Always][HIGH] Error responses do not expose internal implementation details
  - Grep: `traceback|stack_trace|__traceback__` return presence

### Sensitive Data in Error Messages
- [ ] [Always][HIGH] Error messages do not contain DB query/schema information
  - Grep: `(table|column|schema|query).*Exception`
- [ ] [Always][MEDIUM] Review data ID enumeration attack possibility
  - Grep: `Data with ID` -> awareness needed if present

### Rate Limiting
- [ ] [When applicable][MEDIUM] Rate limiting middleware configuration status
  - Detection condition: Check **project-dna.md section 8** "Rate Limiting (slowapi)" status -> [SKIP] if "not implemented"
  - Grep: `RateLimitMiddleware|slowapi|throttle|rate_limit`
  - When not configured: [SKIP] + "Recommend adopting slowapi when expanding endpoints"

### Request Size Limit
- [ ] [When applicable][MEDIUM] Request body size limit configuration status
  - Detection condition: Check **project-dna.md section 8** "File Upload (UploadFile)" status -> [SKIP] if "not implemented"
  - Grep: `max_content_length|body_limit|RequestSizeLimitMiddleware`

## 7. Async Worker Security (Taskiq)

Check worker task files and broker configuration:

### Payload Validation
- [ ] [When applicable][HIGH] Task payload validated via `BasePayload` (not raw `**kwargs` access)
  - Detection condition: Check **project-dna.md section 8** "Taskiq async tasks" status -> [SKIP] if "not implemented"
  - Grep: `@broker.task` -> verify corresponding `BasePayload.model_validate(kwargs)` in function body
- [ ] [When applicable][HIGH] Payload uses `extra="forbid"` (inherited from `PayloadConfig`)
  - Detection condition: Same as above
  - Grep: Payload classes inherit from `BasePayload` (not `BaseModel` or `BaseRequest`)

### Message Security
- [ ] [When applicable][MEDIUM] Sensitive data (PII, credentials) not included in task message payload
  - Detection condition: Same as above
  - Grep: `password|secret|token|ssn|credit` fields in Payload class definitions
- [ ] [When applicable][MEDIUM] Task idempotency considered for retryable operations
  - Detection condition: Same as above
  - Manual review: CUD operations in tasks should handle duplicate execution gracefully

## 8. Object Storage Security (AWS S3)

Check storage client and related configuration files:

### Access Control
- [ ] [When applicable][HIGH] S3 bucket policy does not allow public access
  - Detection condition: Check **project-dna.md section 8** "AWS S3 (aioboto3)" status -> [SKIP] if "not implemented"
  - Manual review: Verify bucket policy configuration in infrastructure/deployment settings
- [ ] [When applicable][HIGH] Pre-signed URL expiration time is appropriately short
  - Detection condition: Same as above
  - Grep: `generate_presigned_url|presigned` -> verify `ExpiresIn` value (recommended: <=3600)

### Upload Validation
- [ ] [When applicable][MEDIUM] Uploaded file Content-Type and size validated server-side before S3 upload
  - Detection condition: Same as above
  - Grep: `content_type|file_size|content_length` validation logic in upload handlers

### Encryption
- [ ] [When applicable][MEDIUM] S3 server-side encryption enabled (SSE-S3 or SSE-KMS)
  - Detection condition: Same as above
  - Grep: `ServerSideEncryption|SSECustomerAlgorithm` in S3 client configuration or put_object calls

## 9. DynamoDB Security

Check DynamoDB client, model, and configuration files:

### Error Information Exposure
- [ ] [When applicable][HIGH] DynamoDB error responses do not expose internal key structure (PK/SK patterns)
  - Detection condition: Check **project-dna.md section 8** "AWS DynamoDB (aioboto3)" status -> [SKIP] if "not implemented"
  - Grep: `DynamoDBNotFoundException` message does not contain composite key format details in production

### Environment Isolation
- [ ] [When applicable][MEDIUM] DynamoDB `endpoint_url` is not `localhost` in production
  - Detection condition: Same as above
  - Grep: `endpoint_url` in Settings -> verify `DYNAMODB_ENDPOINT_URL` is None or AWS endpoint in stg/prod
### Access Control
- [ ] [When applicable][MEDIUM] DynamoDB IAM credentials managed via environment variables (not hardcoded)
  - Detection condition: Same as above
  - Grep: `dynamodb_access_key|dynamodb_secret_key` loaded from `Settings` (not hardcoded strings)
