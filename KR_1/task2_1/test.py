import pytest
from fastapi.testclient import TestClient

from main import app, feedbacks

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_feedbacks():
    """Очищает список отзывов перед каждым тестом, чтобы тесты не влияли друг на друга."""
    feedbacks.clear()
    yield
    feedbacks.clear()


def test_feedback_success():
    response = client.post(
        "/feedback",
        json={"name": "Rustam", "message": "Отличный день! Мне нравится ходить в школу!"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Feedback received. Thank you, Rustam."}


def test_feedback_saved_in_list():
    client.post("/feedback", json={"name": "Катя", "message": "Всё хорошо!"})
    assert len(feedbacks) == 1
    assert feedbacks[0]["name"] == "Катя"
    assert feedbacks[0]["message"] == "Всё хорошо!"


def test_multiple_feedbacks_accumulate():
    client.post("/feedback", json={"name": "Иван", "message": "Первый отзыв"})
    client.post("/feedback", json={"name": "Маша", "message": "Второй отзыв"})
    assert len(feedbacks) == 2


def test_feedback_missing_name():
    response = client.post("/feedback", json={"message": "Сообщение без имени"})
    assert response.status_code == 422


def test_feedback_missing_message():
    response = client.post("/feedback", json={"name": "Иван"})
    assert response.status_code == 422


def test_feedback_empty_body():
    response = client.post("/feedback", json={})
    assert response.status_code == 422