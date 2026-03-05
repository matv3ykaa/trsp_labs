import pytest
from fastapi.testclient import TestClient

from main import app, serializer


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_login_success(client):
    response = client.post("/login", json={"username": "user123", "password": "password123"})
    assert response.status_code == 200
    assert "session_token" in response.cookies


def test_login_wrong_password(client):
    response = client.post("/login", json={"username": "user123", "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/login", json={"username": "ghost", "password": "pass"})
    assert response.status_code == 401


def test_profile_authenticated(client):
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    client.cookies.set("session_token", token)
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user123"
    assert "user_id" in data
    assert data["email"] == "user123@example.com"


def test_profile_no_cookie(client):
    # Свежий клиент, так что никаких кукисов нет, должен вернуть 401
    response = client.get("/profile")
    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_profile_tampered_token(client):
    """Изменённая кукис должна отклоняться"""
    client.cookies.set("session_token", "tampered.fake.value")
    response = client.get("/profile")
    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_profile_token_integrity(client):
    """Обрезанный/изменённый токен, так что BadSignature, поэтому 401"""
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    # Портим последние символы подписи
    broken = token[:-5] + "xxxxx"
    client.cookies.set("session_token", broken)
    response = client.get("/profile")
    assert response.status_code == 401
    