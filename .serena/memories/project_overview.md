# Project Overview

> For tech stack, refer to project-dna.md §8; for layer structure, refer to §1.
> This memory only contains **project-level context** not covered in project-dna.md.

## Purpose
AI Agent Backend Platform built on FastAPI with DDD modular layered architecture

## App Entrypoints
- Server: `src/_apps/server/` — FastAPI (uvicorn)
- Worker: `src/_apps/worker/` — Taskiq (SQS broker)
- Admin: `src/_apps/admin/` — NiceGUI (mounted on server via ui.run_with)

## Dependency Direction
Interface → Application → Domain ← Infrastructure
