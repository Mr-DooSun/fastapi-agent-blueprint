---
name: add-worker-task
argument-hint: domain_name task_name
description: |
  This skill should be used when the user asks to "태스크 추가",
  "워커 태스크", "비동기 작업 추가", "add worker task",
  "background job", "async task", "queue task", "Taskiq 태스크",
  or wants to create a new asynchronous background task for a domain.
---

# 비동기 Worker 태스크 추가

요청: $ARGUMENTS (도메인명과 태스크 설명, 예: "order process_payment")

## 분석

1. 도메인명과 태스크 목적 파악
2. 해당 도메인의 UseCase에 필요한 메서드가 있는지 확인
3. 없으면 `/add-api` 절차의 1~3단계(Repository → Service → UseCase)를 먼저 수행

## 레퍼런스
- `src/user/interface/worker/tasks/user_test_task.py` — 태스크 패턴
- `src/user/interface/worker/bootstrap/user_bootstrap.py` — 워커 부트스트랩 패턴
- `src/_apps/worker/broker.py` — 브로커 설정

## 구현 순서

### 1. 태스크 함수 생성
`src/{name}/interface/worker/tasks/{task_name}_task.py`

```python
from dependency_injector.wiring import Provide, inject
from src._apps.worker.broker import broker
from src.{name}.application.use_cases.{name}_use_case import {Name}UseCase
from src.{name}.domain.dtos.{name}_dto import {Name}DTO
from src.{name}.infrastructure.di.{name}_container import {Name}Container

@broker.task(task_name="{project-name}.{name}.{task_name}")
@inject
async def {task_name}_task(
    {name}_use_case: {Name}UseCase = Provide[{Name}Container.{name}_use_case],
    **kwargs,
) -> None:
    dto = {Name}DTO.model_validate(kwargs)
    await {name}_use_case.{method}(dto=dto)
```

### 2. 워커 부트스트랩 업데이트
`src/{name}/interface/worker/bootstrap/{name}_bootstrap.py`에서:
- 새 태스크 모듈을 import
- `wire(modules=[..., {task_name}_task])` 에 추가

### 3. UseCase 메서드 확인/추가
- 태스크가 호출할 UseCase 메서드가 있는지 확인
- 없으면 UseCase → Service → Repository 순으로 추가

## 핵심 규칙
- 태스크 함수는 thin adapter: `**kwargs` 받아서 DTO 변환 후 UseCase 호출만
- 비즈니스 로직은 반드시 UseCase/Service에 위치
- Model 객체가 태스크에 노출되면 안 됨
- DI 패턴: **project-dna.md §5** 참조
- 변환 패턴: **project-dna.md §6** 참조

## 완료 후 검증
1. pre-commit 실행
2. 브로커 import 확인: `python -c "from src.{name}.interface.worker.tasks.{task_name}_task import {task_name}_task; print('OK')"`
