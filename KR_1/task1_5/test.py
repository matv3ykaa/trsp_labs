from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_adult_user():
    response = client.post("/user", json={"name": "Иван Иванов", "age": 25})
    assert response.status_code == 200
    assert response.json() == {"name": "Иван Иванов", "age": 25, "is_adult": True}


def test_minor_user():
    response = client.post("/user", json={"name": "Петя Петров", "age": 15})
    assert response.status_code == 200
    assert response.json() == {"name": "Петя Петров", "age": 15, "is_adult": False}


def test_exactly_18():
    response = client.post("/user", json={"name": "Аня", "age": 18})
    assert response.status_code == 200
    assert response.json()["is_adult"] is True


def test_missing_name():
    response = client.post("/user", json={"age": 25})
    assert response.status_code == 422


def test_missing_age():
    response = client.post("/user", json={"name": "Иван"})
    assert response.status_code == 422


def test_invalid_age_type():
    response = client.post("/user", json={"name": "Иван", "age": "взрослый"})
    assert response.status_code == 422