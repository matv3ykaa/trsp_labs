from fastapi import FastAPI

from models import User

app = FastAPI()

user = User(name="Иван Иванов", id=1)


@app.get("/")
async def root():
    return {"message": "Добро пожаловать!"}


@app.get("/users")
async def get_user():
    return user
