from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, TaskPriority, TaskStatus
from app.schemas import (
    DashboardResponse,
    StatusTransition,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

VALID_TRANSITIONS = {
    TaskStatus.todo: TaskStatus.in_progress,
    TaskStatus.in_progress: TaskStatus.done,
}


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/search", response_model=list[TaskResponse])
def search_tasks(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    pattern = f"%{q}%"
    tasks = (
        db.query(Task)
        .filter(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
        .all()
    )
    return tasks


@router.get("/stats", response_model=DashboardResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Task.id)).scalar()

    status_rows = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    by_status = {s.value: 0 for s in TaskStatus}
    for status, count in status_rows:
        by_status[status.value] = count

    priority_rows = (
        db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )
    by_priority = {p.value: 0 for p in TaskPriority}
    for priority, count in priority_rows:
        by_priority[priority.value] = count

    overdue = (
        db.query(func.count(Task.id))
        .filter(Task.due_date < date.today(), Task.status != TaskStatus.done)
        .scalar()
    )

    return DashboardResponse(
        total=total, by_status=by_status, by_priority=by_priority, overdue=overdue
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return query.all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.patch("/{task_id}/status", response_model=TaskResponse)
def transition_status(
    task_id: UUID, body: StatusTransition, db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    expected_next = VALID_TRANSITIONS.get(task.status)
    if expected_next != body.status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: cannot move from '{task.status.value}' to '{body.status.value}'",
        )

    task.status = body.status
    db.commit()
    db.refresh(task)
    return task
