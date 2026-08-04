"""Seed the `user` rows the audit tests reference.

`admin_audit_log.admin_user_id` carries `ForeignKey("user.id")`, so every audit
insert in this package needs a matching `user` row. SQLite does not enforce
foreign keys unless `PRAGMA foreign_keys=ON`, so nothing here was needed while
the suite only ran SQLite — and once the PostgreSQL leg was added (#333) these
tests failed with `ForeignKeyViolationError`.

The failure was worse than a missing fixture. `tests/conftest.py::test_db` is
**session-scoped** and truncates nothing between tests, so rows accumulate for
the whole run. In the full suite an unrelated user-domain test happened to
insert `user.id=1` before these ran, and the audit tests passed on that. Run the
package alone, or with `-k`, and five of them failed:

    pytest tests/ -q -k "list_filtered or get_by_id_returns_full_dto"
    -> 5 failed

A leg that is green only because of test ordering is not a leg worth having, so
this fixture makes the package self-contained on any engine.

Note what this does **not** cover. At runtime `admin_user_id` receives an
`admin_identity.id`, not a `user.id` — the FK points at the wrong table since
#218/ADR 049, and on PostgreSQL every production audit write fails and is
swallowed by the logger. That is #348, and it is a schema question, not a test
one. These tests exercise repository mechanics against a valid FK; they are not
evidence that the production path works.
"""

from __future__ import annotations

import pytest_asyncio
from sqlalchemy import select

from src.user.infrastructure.database.models.user_model import UserModel

# Every id these tests attribute an audit row to.
_REFERENCED_USER_IDS = (1, 2, 42)


@pytest_asyncio.fixture(autouse=True)
async def seed_audit_actor_users(test_db):
    """Insert the `user` rows the audit FK requires, once per session.

    Autouse so no test has to remember. Idempotent because `test_db` is
    session-scoped: the second test through finds the rows already present.
    """
    async with test_db.session() as session:
        existing = set(
            (
                await session.execute(
                    select(UserModel.id).where(UserModel.id.in_(_REFERENCED_USER_IDS))
                )
            )
            .scalars()
            .all()
        )
        missing = [i for i in _REFERENCED_USER_IDS if i not in existing]
        for user_id in missing:
            session.add(
                UserModel(
                    id=user_id,
                    username=f"audit-actor-{user_id}",
                    full_name=f"Audit Actor {user_id}",
                    email=f"audit-actor-{user_id}@example.com",
                    password="not-a-real-hash",
                )
            )
        if missing:
            await session.commit()
