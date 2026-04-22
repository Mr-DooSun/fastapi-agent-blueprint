from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text
from src._core.infrastructure.database.database import Base

class TodoModel(Base):
    __tablename__ = "todo"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)