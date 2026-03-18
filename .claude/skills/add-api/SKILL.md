---
name: add-api
argument-hint: "도메인에 METHOD /path 추가"
description: |
  This skill should be used when the user asks to "API 추가",
  "엔드포인트 추가", "add endpoint", "라우터 추가",
  or wants to add a new route to an existing domain.
---

# API 엔드포인트 추가

요청: $ARGUMENTS

## 분석

1. 요청에서 파악: 도메인명, HTTP 메서드, 경로, 목적
2. Serena `find_symbol`로 해당 도메인의 기존 Router, UseCase, Service, Repository 탐색
3. 필요한 것 판단:
   - 새 Request/Response DTO가 필요한가? (기존 것으로 충분한가?)
   - 새 Service 메서드가 필요한가? (BaseRepository 메서드로 충분한가?)
   - 새 UseCase 메서드가 필요한가?
   - 새 Repository 메서드가 필요한가? (커스텀 쿼리가 필요한가?)

## 구현 순서 (Bottom-up)

### 1. Repository (커스텀 쿼리가 필요한 경우만)
- Protocol에 메서드 시그니처 추가: `src/{name}/domain/protocols/{name}_repository_protocol.py`
- Repository에 구현 추가: `src/{name}/infrastructure/repositories/{name}_repository.py`
- BaseRepository 메서드로 충분하면 이 단계 생략

### 2. Service
- `src/{name}/domain/services/{name}_service.py`에 메서드 추가
- Repository 메서드를 호출하는 위임 패턴 유지

### 3. UseCase
- `src/{name}/application/use_cases/{name}_use_case.py`에 메서드 추가
- 목록 조회면 `make_pagination()` 적용
- 비즈니스 로직이 있으면 여기에 추가

### 4. Interface DTO (필요한 경우)
- `src/{name}/interface/server/dtos/{name}_dto.py`에 Request/Response 추가
- Request는 `BaseRequest` 상속, Response는 `BaseResponse` 상속
- **다중상속 금지**

### 5. Router
- `src/{name}/interface/server/routers/{name}_router.py`에 엔드포인트 추가
- Router 패턴: **project-dna.md §9** 참조
- 변환 패턴: **project-dna.md §6** 참조

## 변환 규칙
변환 패턴은 **project-dna.md §6** 참조. import 경로는 **project-dna.md §2** 참조.

## 완료 후 검증
1. pre-commit 실행
2. 해당 도메인 단위 테스트에 새 메서드 테스트 추가
3. 서버 실행 후 Swagger에서 엔드포인트 확인 가능 안내
