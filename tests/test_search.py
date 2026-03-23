def test_search_by_title(client):
    client.post("/tasks", json={"title": "Deploy to production"})
    client.post("/tasks", json={"title": "Write tests"})

    response = client.get("/tasks/search", params={"q": "deploy"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Deploy to production"


def test_search_by_description(client):
    client.post(
        "/tasks",
        json={"title": "Task A", "description": "Fix the authentication bug"},
    )
    client.post("/tasks", json={"title": "Task B", "description": "Add logging"})

    response = client.get("/tasks/search", params={"q": "authentication"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task A"


def test_search_case_insensitive(client):
    client.post("/tasks", json={"title": "URGENT Fix"})

    response = client.get("/tasks/search", params={"q": "urgent"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_no_results(client):
    client.post("/tasks", json={"title": "Something"})

    response = client.get("/tasks/search", params={"q": "nonexistent"})
    assert response.status_code == 200
    assert response.json() == []
