# Project Overview

> 기술 스택은 project-dna.md §8, 레이어 구조는 §1 참조.
> 이 메모리는 project-dna.md에 없는 **프로젝트 수준 컨텍스트**만 담는다.

## 목적
FastAPI DDD 기반 모듈형 레이어드 아키텍처 보일러플레이트

## 앱 엔트리포인트
- Server: `src/_apps/server/` — FastAPI (uvicorn)
- Worker: `src/_apps/worker/` — Taskiq (SQS broker)
- Admin: `src/_apps/admin/` — SQLAdmin

## 의존성 방향
Interface → Application → Domain ← Infrastructure
