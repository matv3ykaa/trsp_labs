import re
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from fastapi import Header

app = FastAPI()

ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[0-9]\.[0-9])?)*$"
)


class CommonHeaders(BaseModel):
    """Модель для переиспользования общих заголовков в разных маршрутах"""
    model_config = {"populate_by_name": True}

    user_agent: str = ""
    accept_language: str = ""

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if v and not ACCEPT_LANGUAGE_RE.match(v):
            raise ValueError("Invalid Accept-Language format")
        return v


async def get_common_headers(
    user_agent: Annotated[str | None, "header"] = None,
    accept_language: Annotated[str | None, "header"] = None,
) -> dict:
    return {"user_agent": user_agent or "", "accept_language": accept_language or ""}


async def common_headers_dep(
    user_agent: str = Header(default=""),
    accept_language: str = Header(default=""),
) -> CommonHeaders:
    return CommonHeaders(user_agent=user_agent, accept_language=accept_language)


@app.get("/headers")
async def get_headers(headers: Annotated[CommonHeaders, Depends(common_headers_dep)]):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@app.get("/info")
async def get_info(headers: Annotated[CommonHeaders, Depends(common_headers_dep)]):
    server_time = datetime.now().isoformat(timespec="seconds")

    response = JSONResponse(
        content={
            "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
            "headers": {
                "User-Agent": headers.user_agent,
                "Accept-Language": headers.accept_language,
            },
        }
    )
    response.headers["X-Server-Time"] = server_time
    return response
