import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


def _utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(SAEnum(TaskPriority), nullable=False, default=TaskPriority.medium)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.todo)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)
