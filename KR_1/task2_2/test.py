import pytest
from fastapi.testclient import TestClient

from main import app, feedbacks

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_feedbacks():
    """Очищает список отзывов перед каждым тестом"""
    feedbacks.clear()
    yield
    feedbacks.clear()


def test_valid_feedback():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Это тяжело, но я справлюсь!"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Спасибо, Артур! Ваш отзыв сохранён."}


def test_feedback_saved():
    client.post("/feedback", json={"name": "Артур", "message": "Это тяжело, но я справлюсь!"})
    assert len(feedbacks) == 1
    assert feedbacks[0]["name"] == "Артур"


def test_name_too_short():
    response = client.post(
        "/feedback",
        json={"name": "А", "message": "Сообщение длиннее десяти символов"},
    )
    assert response.status_code == 422


def test_name_minimum_length():
    response = client.post(
        "/feedback",
        json={"name": "Ян", "message": "Сообщение длиннее десяти символов"},
    )
    assert response.status_code == 200


def test_name_too_long():
    response = client.post(
        "/feedback",
        json={"name": "А" * 51, "message": "Сообщение длиннее десяти символов"},
    )
    assert response.status_code == 422


def test_message_too_short():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Коротко"},
    )
    assert response.status_code == 422


def test_message_minimum_length():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "1234567890"},
    )
    assert response.status_code == 200


def test_message_too_long():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "А" * 501},
    )
    assert response.status_code == 422


def test_banned_word_кринж():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Какой-то кринж у вас тут происходит..."},
    )
    assert response.status_code == 422


def test_banned_word_рофл():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Это просто рофл какой-то, ничего не понятно"},
    )
    assert response.status_code == 422


def test_banned_word_вайб():
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Не тот вайб, совсем не то что ожидалось"},
    )
    assert response.status_code == 422


def test_banned_word_uppercase():
    """Запрещённое слово заглавными буквами."""
    response = client.post(
        "/feedback",
        json={"name": "Артур", "message": "Это КРИНЖ полнейший, я возмущён"},
    )
    assert response.status_code == 422


def test_multiple_errors_name_and_banned_word():
    """Короткое имя + запрещённое слово"""
    response = client.post(
        "/feedback",
        json={"name": "А", "message": "Какой-то кринж у вас тут происходит..."},
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 2