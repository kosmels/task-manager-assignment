from datetime import date, timedelta


def test_create_task_minimal(client):
    response = client.post("/tasks", json={"title": "My task"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My task"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["description"] is None
    assert data["due_date"] is None
    assert "id" in data
    assert "created_at" in data


def test_create_task_full(client):
    future = (date.today() + timedelta(days=7)).isoformat()
    response = client.post(
        "/tasks",
        json={
            "title": "Full task",
            "description": "A detailed description",
            "priority": "high",
            "due_date": future,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Full task"
    assert data["description"] == "A detailed description"
    assert data["priority"] == "high"
    assert data["due_date"] == future


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_task_title_too_long(client):
    response = client.post("/tasks", json={"title": "a" * 201})
    assert response.status_code == 422


def test_create_task_invalid_priority(client):
    response = client.post("/tasks", json={"title": "Test", "priority": "urgent"})
    assert response.status_code == 422


def test_create_task_due_date_in_past(client):
    past = (date.today() - timedelta(days=1)).isoformat()
    response = client.post("/tasks", json={"title": "Test", "due_date": past})
    assert response.status_code == 422


def test_create_task_due_date_today(client):
    today = date.today().isoformat()
    response = client.post("/tasks", json={"title": "Test", "due_date": today})
    assert response.status_code == 422
