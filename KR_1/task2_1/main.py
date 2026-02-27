from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

feedbacks = []


class Feedback(BaseModel):
    name: str
    message: str


@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    feedbacks.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


@app.get("/feedbacks")
async def get_feedbacks():
    return feedbacks
