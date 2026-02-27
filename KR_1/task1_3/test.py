from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_calculate_sum():
    response = client.post(
        "/calculate",
        json={"num1": 5, "num2": 10},
    )
    assert response.status_code == 200
    assert response.json() == {"result": 15.0}


def test_calculate_negative():
    response = client.post(
        "/calculate",
        json={"num1": -3, "num2": 7},
    )
    assert response.status_code == 200
    assert response.json() == {"result": 4.0}


def test_calculate_floats():
    response = client.post(
        "/calculate",
        json={"num1": 1.5, "num2": 2.5},
    )
    assert response.status_code == 200
    assert response.json() == {"result": 4.0}


def test_calculate_invalid_data():
    response = client.post(
        "/calculate",
        json={"num1": "abc", "num2": 10},
    )
    assert response.status_code == 422
    