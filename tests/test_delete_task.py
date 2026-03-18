import uuid


def test_delete_task(client):
    create = client.post("/tasks", json={"title": "To delete"})
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_not_found(client):
    response = client.delete(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404
