from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import SESSION_TTL, RENEW_THRESHOLD, app, create_token, user_sessions, verify_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    user_sessions.clear()
    yield
    user_sessions.clear()


def test_login_success():
    response = client.post("/login", json={"username": "user123", "password": "password123"})
    assert response.status_code == 200
    assert "session_token" in response.cookies


def test_login_wrong_credentials():
    response = client.post("/login", json={"username": "user123", "password": "wrong"})
    assert response.status_code == 401


def test_profile_no_cookie():
    response = client.get("/profile")
    assert response.status_code == 401


def test_profile_tampered_token():
    client.cookies.set("session_token", "fake.tampered.token")
    response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 401


def test_profile_authenticated():
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    client.cookies.set("session_token", token)
    response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 200
    assert response.json()["username"] == "user123"


def test_session_expired():
    """Запрос через 6 минут после логина, тогда 401"""
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    # Сдвигаем время на 6 минут вперёд, то есть SESSION_TTL = 5 мин + 1 минута
    client.cookies.set("session_token", token)
    with patch("main.time.time", return_value=__import__("time").time() + SESSION_TTL + 60):
        response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 401


def test_session_not_renewed_under_3_minutes():
    """Запрос через 2 минуты, тогда кукис не обновляется (в ответе нет Set-Cookie)"""
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    client.cookies.set("session_token", token)
    with patch("main.time.time", return_value=__import__("time").time() + 120):
        response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 200
    # Кукис не должен обновляться
    assert "session_token" not in response.cookies


def test_session_renewed_after_3_minutes():
    """Запрос через 4 минуты, тогда кукис обновляется"""
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]

    client.cookies.set("session_token", token)
    with patch("main.time.time", return_value=__import__("time").time() + RENEW_THRESHOLD + 30):
        response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 200
    assert "session_token" in response.cookies
    assert response.cookies["session_token"] != token  # токен изменился


def test_tampered_user_id_blocked():
    """Подмена user_id → невалидная подпись, тогда 401"""
    import time as t
    ts = str(int(t.time()))
    # Создаём токен с другим user_id, который не совпадает с подписью
    broken = f"00000000-fake-fake-fake.{ts}.invalidsig"
    client.cookies.set("session_token", broken)
    response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 401


def test_tampered_timestamp_blocked():
    """Изменение timestamp, тогда подпись не совпадает, следоватеьно 401"""
    login_resp = client.post("/login", json={"username": "user123", "password": "password123"})
    token = login_resp.cookies["session_token"]
    parts = token.split(".")
    # Меняем timestamp на другое значение
    parts[1] = "0000000000"
    broken_token = ".".join(parts)
    client.cookies.set("session_token", broken_token)
    response = client.get("/profile")
    client.cookies.clear()
    assert response.status_code == 401
    