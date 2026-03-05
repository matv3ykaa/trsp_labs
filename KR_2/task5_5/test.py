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


def test_headers_empty_defaults():
    """Без заголовков, тогда возвращаем пустые строки (default="")"""
    response = client.get("/headers", headers={"User-Agent": "", "Accept-Language": ""})
    assert response.status_code == 200


def test_info_body():
    response = client.get(
        "/info",
        headers={"User-Agent": VALID_UA, "Accept-Language": VALID_LANG},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Добро пожаловать! Ваши заголовки успешно обработаны."
    assert data["headers"]["User-Agent"] == VALID_UA
    assert data["headers"]["Accept-Language"] == VALID_LANG


def test_info_x_server_time_header():
    """Ответ должен содержать заголовок X-Server-Time"""
    response = client.get(
        "/info",
        headers={"User-Agent": VALID_UA, "Accept-Language": VALID_LANG},
    )
    assert response.status_code == 200
    assert "x-server-time" in response.headers  # HTTP-заголовки case-insensitive


def test_info_x_server_time_format():
    """X-Server-Time должен быть в ISO формате"""
    from datetime import datetime
    response = client.get(
        "/info",
        headers={"User-Agent": VALID_UA, "Accept-Language": VALID_LANG},
    )
    server_time = response.headers.get("x-server-time")
    # Проверяем, что парсится как datetime, и если формат неверный, будет выброшено исключение
    datetime.fromisoformat(server_time)


def test_both_routes_accept_same_headers():
    """Убеждаемся, что оба маршрута принимают одинаковые заголовки"""
    headers = {"User-Agent": VALID_UA, "Accept-Language": VALID_LANG}

    r1 = client.get("/headers", headers=headers)
    r2 = client.get("/info", headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200
    # Оба маршрута вернули одинаковые данные о заголовках
    assert r1.json()["User-Agent"] == r2.json()["headers"]["User-Agent"]
    assert r1.json()["Accept-Language"] == r2.json()["headers"]["Accept-Language"]