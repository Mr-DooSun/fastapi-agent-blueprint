"""Taskiq middleware that wires structlog context for every task run (#9).

On ``pre_execute`` the middleware binds the task identifier into the
current async context so every log emitted from within the task
carries ``taskiq_task_id`` / ``taskiq_task_name``. If the dispatcher
attached a ``correlation_id`` label (e.g. the HTTP request that kicked
the task), it is re-bound here too — that's how request → task
correlation is preserved across the process boundary.

On ``post_execute`` the keys this middleware owns are cleared so the
next task picked up by the same worker loop starts with a clean
context. Middleware registration:

```python
# src/_apps/worker/app.py
broker.add_middlewares(StructlogContextMiddleware())
```

Dispatcher side, pass the correlation ID through labels:

```python
await my_task.kicker().with_labels(
    correlation_id=correlation_id.get() or "",
).kiq(arg)
```

Background: https://github.com/orgs/taskiq-python/discussions/273
"""

from __future__ import annotations

from typing import Any

import structlog
from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult


class StructlogContextMiddleware(TaskiqMiddleware):
    """Bind/unbind task-scoped context for structured logging."""

    async def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        # Wipe anything that leaked from the previous task on this loop.
        structlog.contextvars.clear_contextvars()

        bindings: dict[str, Any] = {
            "taskiq_task_id": message.task_id,
            "taskiq_task_name": message.task_name,
        }
        correlation_id = message.labels.get("correlation_id")
        if correlation_id:
            bindings["correlation_id"] = correlation_id
        structlog.contextvars.bind_contextvars(**bindings)
        return message

    async def post_execute(
        self, message: TaskiqMessage, result: TaskiqResult[Any]
    ) -> None:
        structlog.contextvars.clear_contextvars()
