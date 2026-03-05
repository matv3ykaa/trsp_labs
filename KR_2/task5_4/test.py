from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
VALID_LANG = "en-US,en;q=0.9,es;q=0.8"


def test_headers_success():
    response = client.get(
        "/headers",
        headers={"User-Agent": VALID_UA, "Accept-Language": VALID_LANG},
    )
    assert response.status_code == 200
    assert response.json() == {"User-Agent": VALID_UA, "Accept-Language": VALID_LANG}


def test_missing_accept_language():
    response = client.get("/headers", headers={"User-Agent": VALID_UA})
    assert response.status_code == 400
    assert "Accept-Language" in response.json()["detail"]


def test_missing_user_agent():
    # TestClient автоматически добавляет User-Agent, явно заменяем пустым
    response = client.get(
        "/headers",
        headers={"User-Agent": "", "Accept-Language": VALID_LANG},
    )
    assert response.status_code == 400


def test_invalid_accept_language_format():
    response = client.get(
        "/headers",
        headers={"User-Agent": VALID_UA, "Accept-Language": "%%invalid%%"},
    )
    assert response.status_code == 400
    assert "Accept-Language" in response.json()["detail"]


def test_simple_accept_language():
    """Простой формат en тоже должен работать"""
    response = client.get(
        "/headers",
        headers={"User-Agent": VALID_UA, "Accept-Language": "en"},
    )
    assert response.status_code == 200