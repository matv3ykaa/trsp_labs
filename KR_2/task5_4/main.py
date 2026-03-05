import re

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

# Паттерн для проверки формата Accept-Language, по типу en-US,en;q=0.9,es;q=0.8
ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[0-9]\.[0-9])?)*$"
)


@app.get("/headers")
async def get_headers(request: Request):
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")

    if not user_agent:
        raise HTTPException(status_code=400, detail="Missing User-Agent header")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Missing Accept-Language header")

    # Опциональная проверка формата Accept-Language
    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
    }
