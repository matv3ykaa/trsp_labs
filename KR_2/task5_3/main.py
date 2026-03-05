import hashlib
import hmac
import time
import uuid

from fastapi import Cookie, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "super-secret-key-please-change-in-production-i-was-too-lazy-to-generate-a-real-one-and-put-it-in-.env"

SESSION_TTL = 300        # максимальное время жизни без активности
RENEW_THRESHOLD = 180    # обновлять кукис если прошло >= 3 и < 5 минут

USERS = {
    "user123": {"password": "password123", "email": "user123@example.com"},
    "admin":   {"password": "admin",        "email": "admin@example.com"},
}

def _sign(user_id: str, timestamp: str) -> str:
    """HMAC-SHA256 подпись для пары user_id + timestamp"""
    message = f"{user_id}.{timestamp}".encode()
    return hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()


def create_token(user_id: str) -> str:
    """Создаёт токен вида: <user_id>.<timestamp>.<signature>"""
    ts = str(int(time.time()))
    sig = _sign(user_id, ts)
    return f"{user_id}.{ts}.{sig}"


def verify_token(token: str) -> dict | None:
    """
    Проверяет токен. Возвращает словарь с user_id и last_active,
    либо None если токен невалиден или просрочен
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None  # Неверный формат токена
    
    user_id, ts, sig = parts
    expected_sig = _sign(user_id, ts)

    if not hmac.compare_digest(sig, expected_sig):
        return None  # Подпись не совпадает, следовательно подделка

    last_active = int(ts)
    elapsed = time.time() - last_active

    if elapsed >= SESSION_TTL:
        return None  # Сессия истекла

    return {"user_id": user_id, "last_active": last_active, "elapsed": elapsed}


class LoginData(BaseModel):
    username: str
    password: str


# Хранилище user_id, username
user_sessions: dict[str, str] = {}


@app.post("/login")
async def login(data: LoginData):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        return JSONResponse(status_code=401, content={"message": "Invalid credentials"})

    user_id = str(uuid.uuid4())
    user_sessions[user_id] = data.username
    token = create_token(user_id)

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=SESSION_TTL,
    )
    return response


@app.get("/profile")
async def get_profile(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        return JSONResponse(status_code=401, content={"message": "Invalid session"})

    session = verify_token(session_token)
    if session is None:
        return JSONResponse(status_code=401, content={"message": "Session expired"})

    user_id = session["user_id"]
    username = user_sessions.get(user_id)
    if not username:
        return JSONResponse(status_code=401, content={"message": "Invalid session"})

    user = USERS[username]
    result = {
        "user_id": user_id,
        "username": username,
        "email": user["email"],
    }

    # Обновляем кукис если прошло >= 3 минут (RENEW_THRESHOLD), но < 5 минут
    response = JSONResponse(content=result)
    if session["elapsed"] >= RENEW_THRESHOLD:
        new_token = create_token(user_id)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=SESSION_TTL,
        )
    return response
