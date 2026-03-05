import uuid

from fastapi import Cookie, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# {session_token: username}
active_sessions: dict[str, str] = {}

USERS = {
    "user123": "password123",
    "admin":   "admin",
}


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginData):
    if USERS.get(data.username) != data.password:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid credentials"},
        )

    token = str(uuid.uuid4())
    active_sessions[token] = data.username

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=300, # Тут в секундах, то есть 5 минут
    )
    return response


@app.get("/user")
async def get_user(session_token: str | None = Cookie(default=None)):
    if session_token is None or session_token not in active_sessions:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"},
        )

    username = active_sessions[session_token]
    return {
        "username": username,
        "profile": f"Профиль пользователя {username}",
    }


@app.post("/logout")
async def logout(session_token: str | None = Cookie(default=None)):
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_token")
    return response
