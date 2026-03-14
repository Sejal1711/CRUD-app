from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import Task, User
from app.schemas.task import (
    TaskOut, CreateTaskRequest, UpdateTaskRequest,
    TaskStatus, TaskPriority, TaskStatsOut,
)
from app.utils.dependencies import get_current_user
from app.utils.response import success
from app.utils.sanitize import sanitize

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/stats", summary="Get task statistics")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task)
    if current_user.role != "ADMIN":
        query = query.filter(Task.userId == current_user.id)

    total = query.count()

    by_status = (
        query.with_entities(Task.status, func.count(Task.status))
        .group_by(Task.status).all()
    )
    by_priority = (
        query.with_entities(Task.priority, func.count(Task.priority))
        .group_by(Task.priority).all()
    )

    return success({
        "stats": {
            "total":      total,
            "byStatus":   {s: c for s, c in by_status},
            "byPriority": {p: c for p, c in by_priority},
        }
    })


@router.get("", summary="Get all tasks")
def get_tasks(
    page:     int           = Query(1, ge=1),
    limit:    int           = Query(10, ge=1, le=100),
    status:   Optional[TaskStatus]   = None,
    priority: Optional[TaskPriority] = None,
    search:   Optional[str] = None,
    sortBy:   str           = Query("createdAt", pattern="^(createdAt|dueDate|priority|title)$"),
    order:    str           = Query("desc",      pattern="^(asc|desc)$"),
    db:       Session       = Depends(get_db),
    current_user: User      = Depends(get_current_user),
):
    query = db.query(Task)

    if current_user.role != "ADMIN":
        query = query.filter(Task.userId == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if search:
        query = query.filter(
            Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
        )

    total = query.count()
    col = getattr(Task, sortBy)
    query = query.order_by(col.desc() if order == "desc" else col.asc())
    tasks = query.offset((page - 1) * limit).limit(limit).all()

    return success({
        "tasks": [TaskOut.model_validate(t).model_dump(mode="json") for t in tasks],
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "pages": -(-total // limit),  # ceiling division
        },
    })


@router.get("/{task_id}", summary="Get task by ID")
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "ADMIN" and task.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return success({"task": TaskOut.model_validate(task).model_dump(mode="json")})


@router.post("", summary="Create a new task", status_code=201)
def create_task(
    body: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean = sanitize(body.model_dump(mode="json"))
    task = Task(**clean, userId=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)

    return success(
        {"task": TaskOut.model_validate(task).model_dump(mode="json")},
        message="Task created",
        status_code=201,
    )


@router.patch("/{task_id}", summary="Update a task")
def update_task(
    task_id: str,
    body: UpdateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "ADMIN" and task.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updates = sanitize({k: v for k, v in body.model_dump(mode="json").items() if v is not None})
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    for key, val in updates.items():
        setattr(task, key, val)

    db.commit()
    db.refresh(task)
    return success({"task": TaskOut.model_validate(task).model_dump(mode="json")}, message="Task updated")


@router.delete("/{task_id}", summary="Delete a task")
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "ADMIN" and task.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(task)
    db.commit()
    return success(message="Task deleted")
