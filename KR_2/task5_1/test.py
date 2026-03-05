import pytest
from fastapi.testclient import TestClient

from main import app, active_sessions

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    active_sessions.clear()
    yield
    active_sessions.clear()


def test_login_success():
    response = client.post("/login", json={"username": "user123", "password": "password123"})
    assert response.status_code == 200
    assert "session_token" in response.cookies


def test_login_wrong_password():
    response = client.post("/login", json={"username": "user123", "password": "wrongpass"})
    assert response.status_code == 401
    assert "session_token" not in response.cookies


def test_login_unknown_user():
    response = client.post("/login", json={"username": "nobody", "password": "pass"})
    assert response.status_code == 401


def test_get_user_authenticated():
    # Сначала логинимся
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    # Запрашиваем профиль с кукисом
    client.cookies.set("session_token", token)
    response = client.get("/user")
    client.cookies.clear()
    assert response.status_code == 200
    assert response.json()["username"] == "user123"


def test_get_user_no_cookie():
    response = client.get("/user")
    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_get_user_invalid_token():
    client.cookies.set("session_token", "invalid_token_value")
    response = client.get("/user")
    client.cookies.clear()
    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_logout_clears_session():
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    client.cookies.set("session_token", token)
    client.post("/logout")
    client.cookies.clear()

    # После логаута токен больше не работает
    client.cookies.set("session_token", token)
    response = client.get("/user")
    client.cookies.clear()
    assert response.status_code == 401
    