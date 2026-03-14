import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.config.database import Base

# Named enums required by PostgreSQL
role_enum     = Enum("USER", "ADMIN",                  name="role")
status_enum   = Enum("TODO", "IN_PROGRESS", "DONE",    name="taskstatus")
priority_enum = Enum("LOW",  "MEDIUM", "HIGH",         name="taskpriority")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id        = Column(String(36),  primary_key=True, default=new_uuid)
    name      = Column(String(100), nullable=False)
    email     = Column(String(255), unique=True, nullable=False, index=True)
    password  = Column(String(255), nullable=False)
    role      = Column(role_enum,   default="USER", nullable=False)
    createdAt = Column(DateTime, default=utcnow)
    updatedAt = Column(DateTime, default=utcnow, onupdate=utcnow)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(String(36),    primary_key=True, default=new_uuid)
    title       = Column(String(100),   nullable=False)
    description = Column(Text,          nullable=True)
    status      = Column(status_enum,   default="TODO",   nullable=False)
    priority    = Column(priority_enum, default="MEDIUM", nullable=False)
    dueDate     = Column(DateTime,      nullable=True)
    createdAt   = Column(DateTime,      default=utcnow)
    updatedAt   = Column(DateTime,      default=utcnow, onupdate=utcnow)

    userId = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user   = relationship("User", back_populates="tasks")

    __table_args__ = (
        Index("ix_tasks_userId",          "userId"),
        Index("ix_tasks_userId_status",   "userId", "status"),
        Index("ix_tasks_userId_priority", "userId", "priority"),
        Index("ix_tasks_status_priority", "status", "priority"),
        Index("ix_tasks_createdAt",       "createdAt"),
    )
