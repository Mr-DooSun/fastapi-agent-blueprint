"""Keep the production audit-actor defect visible in the suite (#348).

Every other DB-touching test in this package writes `admin_user_id=None`,
because `project-dna.md` §17 IC-218-1 says "No admin row may exist in `user`"
and `admin_audit_log.admin_user_id` still carries `ForeignKey("user.id")`. There
is no honest non-null value to write until #348 decides where that FK should
point.

Writing NULL everywhere would make the package pass on both engines and leave
nothing in the suite that knows the production path is broken. This file is that
something.

At runtime the actor id is an `admin_identity.id`
(`AdminAuthUseCase._admin_session_for` sets `user_id=admin.id`, and
`AdminAuditLogger` reads it back from the session), so on PostgreSQL the insert
below is exactly what production attempts — and it fails the constraint. The
production logger swallows that exception (`# noqa: BLE001 - swallowed by
design`), which is why the breakage is invisible outside a test like this one.

`strict=True` is the point: when #348 lands, this XPASSes, CI fails, and whoever
fixed it is told to come back here and turn it into a real assertion instead of
leaving a stale marker behind.
"""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from sqlalchemy import select

from src._core.infrastructure.admin.audit import (
    AdminAction,
    AdminAuditLogRepository,
    AuditLogDTO,
    AuditResult,
)
from src._core.infrastructure.admin.audit.models.audit_log_model import AdminAuditLog
from src.admin_identity.infrastructure.database.models.admin_identity_model import (
    AdminIdentityModel,
)
from src.user.infrastructure.database.models.user_model import UserModel

_ON_POSTGRESQL = os.environ.get("TEST_DB_ENGINE", "sqlite").lower() == "postgresql"

_pytestmark_reason = (
    "admin_audit_log.admin_user_id FKs to user.id while runtime writes an "
    "admin_identity.id (#348). SQLite does not enforce foreign keys, so this "
    "only fails on the engine production uses."
)


# An explicit, deliberately out-of-range id. With an autoincrement id this test
# is order-dependent and unusable: `tests/conftest.py::test_db` is session-scoped
# and truncates nothing, so whether the new admin's id collides with a `user.id`
# some earlier test happened to create decides whether the FK is satisfied. That
# is not hypothetical — the first version of this file XPASSed in the full suite
# (strict=True turned that into a failure) while xfailing when the package ran
# alone. Nothing in the suite inserts a user this far up.
_PROBE_ADMIN_ID = 900_001


@pytest_asyncio.fixture
async def admin_identity_row(test_db):
    """A real admin whose id is what production would attribute an action to."""
    async with test_db.session() as session:
        colliding_user = (
            await session.execute(
                select(UserModel.id).where(UserModel.id == _PROBE_ADMIN_ID)
            )
        ).scalar_one_or_none()
        assert colliding_user is None, (
            f"a user row exists at id {_PROBE_ADMIN_ID}, which would satisfy the "
            "FK by accident and make this probe meaningless"
        )

        existing = (
            await session.execute(
                select(AdminIdentityModel).where(
                    AdminIdentityModel.id == _PROBE_ADMIN_ID
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing.id

        admin = AdminIdentityModel(
            id=_PROBE_ADMIN_ID,
            username="audit-fk-probe",
            full_name="Audit FK Probe",
            email="audit-fk-probe@example.com",
            password="not-a-real-hash",
        )
        session.add(admin)
        await session.commit()
        return admin.id


@pytest.mark.xfail(_ON_POSTGRESQL, reason=_pytestmark_reason, strict=True)
@pytest.mark.asyncio
async def test_audit_write_accepts_an_admin_identity_actor(test_db, admin_identity_row):
    repo = AdminAuditLogRepository(test_db)

    await repo.insert(
        AuditLogDTO(
            admin_user_id=admin_identity_row,
            admin_username="audit-fk-probe",
            action=AdminAction.LOGIN,
            domain="auth",
            result=AuditResult.SUCCESS,
        )
    )

    async with test_db.session() as session:
        stored = (
            (
                await session.execute(
                    select(AdminAuditLog).where(
                        AdminAuditLog.admin_username == "audit-fk-probe"
                    )
                )
            )
            .scalars()
            .all()
        )

    assert len(stored) == 1
    assert stored[0].admin_user_id == admin_identity_row
