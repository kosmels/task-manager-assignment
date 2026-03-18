def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_by_status(client):
    create = client.post("/tasks", json={"title": "Todo task"})
    task_id = create.json()["id"]
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})

    client.post("/tasks", json={"title": "Another todo"})

    response = client.get("/tasks", params={"status": "in_progress"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Todo task"


def test_filter_by_priority(client):
    client.post("/tasks", json={"title": "High", "priority": "high"})
    client.post("/tasks", json={"title": "Low", "priority": "low"})

    response = client.get("/tasks", params={"priority": "high"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High"


def test_filter_by_status_and_priority(client):
    client.post("/tasks", json={"title": "High todo", "priority": "high"})
    client.post("/tasks", json={"title": "Low todo", "priority": "low"})

    response = client.get("/tasks", params={"status": "todo", "priority": "high"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High todo"
