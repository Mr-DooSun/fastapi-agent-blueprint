"""Tests for the Taskiq structlog-context middleware (#9)."""

from __future__ import annotations

import pytest
import structlog
from taskiq import TaskiqMessage, TaskiqResult

from src._core.infrastructure.logging.taskiq_middleware import (
    StructlogContextMiddleware,
)


@pytest.fixture(autouse=True)
def _cleanup_contextvars():
    yield
    structlog.contextvars.clear_contextvars()


def _make_message(
    *,
    task_id: str = "t_1",
    task_name: str = "sample_task",
    labels: dict[str, str] | None = None,
) -> TaskiqMessage:
    return TaskiqMessage(
        task_id=task_id,
        task_name=task_name,
        labels=labels or {},
        labels_types=None,
        args=[],
        kwargs={},
    )


class TestStructlogContextMiddleware:
    @pytest.mark.asyncio
    async def test_pre_execute_binds_task_metadata(self):
        mw = StructlogContextMiddleware()
        await mw.pre_execute(_make_message(task_id="abc", task_name="do_thing"))

        ctx = structlog.contextvars.get_contextvars()
        assert ctx["taskiq_task_id"] == "abc"
        assert ctx["taskiq_task_name"] == "do_thing"

    @pytest.mark.asyncio
    async def test_pre_execute_binds_correlation_id_from_labels(self):
        mw = StructlogContextMiddleware()
        await mw.pre_execute(_make_message(labels={"correlation_id": "req_parent_123"}))

        ctx = structlog.contextvars.get_contextvars()
        assert ctx["correlation_id"] == "req_parent_123"

    @pytest.mark.asyncio
    async def test_pre_execute_omits_correlation_id_when_absent(self):
        mw = StructlogContextMiddleware()
        await mw.pre_execute(_make_message(labels={}))

        ctx = structlog.contextvars.get_contextvars()
        assert "correlation_id" not in ctx

    @pytest.mark.asyncio
    async def test_pre_execute_clears_stale_context_from_previous_task(self):
        """Prev-task leakage guard — critical when a worker loop reuses tasks."""
        structlog.contextvars.bind_contextvars(leftover="stale_value")

        mw = StructlogContextMiddleware()
        await mw.pre_execute(_make_message(task_id="fresh"))

        ctx = structlog.contextvars.get_contextvars()
        assert "leftover" not in ctx
        assert ctx["taskiq_task_id"] == "fresh"

    @pytest.mark.asyncio
    async def test_post_execute_clears_context(self):
        mw = StructlogContextMiddleware()
        await mw.pre_execute(_make_message())

        await mw.post_execute(
            _make_message(),
            TaskiqResult(
                is_err=False,
                return_value=None,
                execution_time=0.0,
                labels={},
                error=None,
                log=None,
            ),
        )

        assert structlog.contextvars.get_contextvars() == {}
