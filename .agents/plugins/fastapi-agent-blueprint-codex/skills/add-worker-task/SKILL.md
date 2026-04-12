---
name: add-worker-task
description: Add a Taskiq worker task with an explicit payload contract, thin task adapter, and Service-owned business logic.
metadata:
  short-description: Add async worker task
---

# Add Worker Task

1. Read `AGENTS.md` and `docs/ai/shared/project-dna.md`.
2. Confirm the target Service method exists; add it first if needed.
3. Add:
   - payload schema under `interface/worker/payloads/`
   - task under `interface/worker/tasks/`
   - bootstrap wiring under `interface/worker/bootstrap/`
4. Keep the task thin: validate payload, then call the Service.
5. Use Payload when the worker message contract differs from HTTP Request/Response.
6. Verify imports and run targeted checks on the new worker files.
