from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    TODO        = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE        = "DONE"


class TaskPriority(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


class TaskOwner(BaseModel):
    id:    str
    name:  str
    email: str
    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id:          str
    title:       str
    description: Optional[str]
    status:      TaskStatus
    priority:    TaskPriority
    dueDate:     Optional[datetime]
    createdAt:   datetime
    updatedAt:   datetime
    user:        TaskOwner
    model_config = {"from_attributes": True}


class CreateTaskRequest(BaseModel):
    title:       str
    description: Optional[str] = None
    status:      TaskStatus    = TaskStatus.TODO
    priority:    TaskPriority  = TaskPriority.MEDIUM
    dueDate:     Optional[datetime] = None


class UpdateTaskRequest(BaseModel):
    title:       Optional[str]           = None
    description: Optional[str]           = None
    status:      Optional[TaskStatus]    = None
    priority:    Optional[TaskPriority]  = None
    dueDate:     Optional[datetime]      = None


class TaskStatsOut(BaseModel):
    total:      int
    byStatus:   dict
    byPriority: dict
