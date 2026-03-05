import uuid

from fastapi import Cookie, FastAPI
from fastapi.responses import JSONResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "super-secret-key-change-in-production"
serializer = URLSafeSerializer(SECRET_KEY)

USERS = {
    "user123": {"password": "password123", "email": "user123@example.com"},
    "admin":   {"password": "admin",        "email": "admin@example.com"},
}


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginData):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        return JSONResponse(status_code=401, content={"message": "Invalid credentials"})

    user_id = str(uuid.uuid4())
    # Подписываем user_id секретным ключом
    token = serializer.dumps({"user_id": user_id, "username": data.username})

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=300,
    )
    return response


@app.get("/profile")
async def get_profile(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    try:
        # Проверяем подпись, если кукис изменен, то бросит BadSignature
        data = serializer.loads(session_token)
    except (BadSignature, SignatureExpired):
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    username = data["username"]
    user = USERS.get(username, {})
    return {
        "user_id": data["user_id"],
        "username": username,
        "email": user.get("email"),
    }
