from datetime import date, timedelta


def test_stats_empty(client):
    response = client.get("/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["by_status"] == {"todo": 0, "in_progress": 0, "done": 0}
    assert data["by_priority"] == {"low": 0, "medium": 0, "high": 0}
    assert data["overdue"] == 0


def test_stats_with_tasks(client):
    client.post("/tasks", json={"title": "T1", "priority": "high"})
    client.post("/tasks", json={"title": "T2", "priority": "low"})
    t3 = client.post("/tasks", json={"title": "T3", "priority": "medium"})
    task_id = t3.json()["id"]
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})

    response = client.get("/tasks/stats")
    data = response.json()
    assert data["total"] == 3
    assert data["by_status"]["todo"] == 2
    assert data["by_status"]["in_progress"] == 1
    assert data["by_priority"]["high"] == 1
    assert data["by_priority"]["low"] == 1
    assert data["by_priority"]["medium"] == 1


def test_stats_overdue(client, db_session):
    from app.models import Task, TaskPriority, TaskStatus

    # Insert a task with a past due date directly (bypassing API validation)
    overdue_task = Task(
        title="Overdue",
        priority=TaskPriority.high,
        status=TaskStatus.todo,
        due_date=date.today() - timedelta(days=1),
    )
    db_session.add(overdue_task)
    db_session.flush()

    # A done task with past due date should NOT count as overdue
    done_task = Task(
        title="Done overdue",
        priority=TaskPriority.medium,
        status=TaskStatus.done,
        due_date=date.today() - timedelta(days=1),
    )
    db_session.add(done_task)
    db_session.flush()

    # A task with no due date is never overdue
    client.post("/tasks", json={"title": "No due date"})

    response = client.get("/tasks/stats")
    data = response.json()
    assert data["overdue"] == 1
    assert data["total"] == 3
