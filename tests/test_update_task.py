import uuid
from datetime import date, timedelta


def test_update_title(client):
    create = client.post("/tasks", json={"title": "Original"})
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_update_description(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"description": "New desc"})
    assert response.status_code == 200
    assert response.json()["description"] == "New desc"
    assert response.json()["title"] == "Task"  # unchanged


def test_update_priority(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"priority": "high"})
    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_update_due_date(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    future = (date.today() + timedelta(days=30)).isoformat()
    response = client.put(f"/tasks/{task_id}", json={"due_date": future})
    assert response.status_code == 200
    assert response.json()["due_date"] == future


def test_update_not_found(client):
    response = client.put(f"/tasks/{uuid.uuid4()}", json={"title": "Nope"})
    assert response.status_code == 404


def test_update_does_not_change_status(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    # PUT body with no status field — status should remain "todo"
    response = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
    assert response.json()["status"] == "todo"
