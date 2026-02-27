import re

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

feedbacks = []

BANNED_WORDS_PATTERN = re.compile(
    r"(кринж|рофл|вайб)",
    re.IGNORECASE,
)


class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def check_banned_words(cls, value: str) -> str:
        if BANNED_WORDS_PATTERN.search(value):
            raise ValueError("Использование недопустимых слов")
        return value


@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    feedbacks.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}


@app.get("/feedbacks")
async def get_feedbacks():
    return feedbacks
