from datetime import UTC, datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from src._core.infrastructure.persistence.rdb.database import Base


class TodoModel(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
