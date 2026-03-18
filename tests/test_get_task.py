import uuid


def test_get_task(client):
    create = client.post("/tasks", json={"title": "Lookup task"})
    task_id = create.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Lookup task"


def test_get_task_not_found(client):
    response = client.get(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404
