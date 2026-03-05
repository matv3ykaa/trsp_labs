from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_user_full():
    response = client.post(
        "/create_user",
        json={"name": "Alice", "email": "alice@example.com", "age": 30, "is_subscribed": True},
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "is_subscribed": True,
    }


def test_create_user_required_only():
    """age и is_subscribed это необязательные поля, поэтому их можно не указывать"""
    response = client.post(
        "/create_user",
        json={"name": "Bob", "email": "bob@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bob"
    assert data["age"] is None
    assert data["is_subscribed"] is None


def test_invalid_email():
    response = client.post(
        "/create_user",
        json={"name": "Alice", "email": "not-an-email"},
    )
    assert response.status_code == 422


def test_negative_age():
    response = client.post(
        "/create_user",
        json={"name": "Alice", "email": "alice@example.com", "age": -5},
    )
    assert response.status_code == 422


def test_zero_age():
    response = client.post(
        "/create_user",
        json={"name": "Alice", "email": "alice@example.com", "age": 0},
    )
    assert response.status_code == 422


def test_missing_name():
    response = client.post(
        "/create_user",
        json={"email": "alice@example.com"},
    )
    assert response.status_code == 422


def test_missing_email():
    response = client.post(
        "/create_user",
        json={"name": "Alice"},
    )
    assert response.status_code == 422