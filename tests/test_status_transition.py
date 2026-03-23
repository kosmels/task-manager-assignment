import uuid


def test_todo_to_in_progress(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_in_progress_to_done(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_todo_to_done_invalid(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert response.status_code == 400


def test_done_to_in_progress_invalid(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert response.status_code == 400


def test_in_progress_to_todo_invalid(client):
    create = client.post("/tasks", json={"title": "Task"})
    task_id = create.json()["id"]

    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "todo"})
    assert response.status_code == 400


def test_transition_not_found(client):
    response = client.patch(
        f"/tasks/{uuid.uuid4()}/status", json={"status": "in_progress"}
    )
    assert response.status_code == 404
