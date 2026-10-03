"""FastAPI backend and static frontend for the LLM chat practice app."""

import logging
import os
import re
import threading
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from uuid import UUID, uuid4

import mysql.connector
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mysql.connector import Error as MySQLError
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    AuthenticationError,
    RateLimitError,
)
from pydantic import BaseModel, Field, field_validator

from practice import BASE_URL, DEMO_MODE, MODEL, PROVIDER, ask_model

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "genai_chat_practice")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
SESSION_COOKIE = "practice_chat_session"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
MAX_CONTEXT_MESSAGES = 20
logger = logging.getLogger(__name__)
chat_lock = threading.Lock()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Enter a message before sending.")
        return value


class ChatReply(BaseModel):
    reply: str


class ChatHistory(BaseModel):
    messages: list[dict[str, str]]


def connect_database(database: str | None = MYSQL_DATABASE):
    settings: dict[str, str | int] = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "connection_timeout": 10,
        "charset": "utf8mb4",
    }
    if database is not None:
        settings["database"] = database
    return mysql.connector.connect(**settings)


@contextmanager
def database_connection(*, server: bool = False) -> Generator:
    connection = connect_database(None if server else MYSQL_DATABASE)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    if not re.fullmatch(r"[A-Za-z0-9_]+", MYSQL_DATABASE):
        raise RuntimeError(
            "MYSQL_DATABASE must contain only letters, numbers, and underscores."
        )

    with database_connection(server=True) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        finally:
            cursor.close()

    with database_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    session_id CHAR(36) NOT NULL,
                    role VARCHAR(16) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_chat_messages_session (session_id, id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        finally:
            cursor.close()


def get_session_id(request: Request) -> str:
    return request.state.session_id


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        initialize_database()
    except MySQLError as error:
        logger.exception("Could not initialize the MySQL chat database.")
        raise RuntimeError(
            "Could not connect to MySQL. Check MYSQL_HOST, MYSQL_DATABASE, "
            "MYSQL_USER, and MYSQL_PASSWORD in .env.local."
        ) from error
    yield


app = FastAPI(
    title="LLM Chat Practice",
    description="A local learning app connecting a browser, FastAPI, MySQL, and an LLM provider.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.middleware("http")
async def set_chat_session(request: Request, call_next) -> Response:
    session_id = request.cookies.get(SESSION_COOKIE)
    try:
        UUID(session_id or "")
    except ValueError:
        session_id = str(uuid4())
        request.state.new_session = True
    else:
        request.state.new_session = False
    request.state.session_id = session_id

    response = await call_next(request)
    if request.state.new_session:
        response.set_cookie(
            SESSION_COOKIE,
            session_id,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
            path="/",
        )
    return response


@app.get("/", response_class=FileResponse, include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "provider": PROVIDER,
        "model": MODEL,
        "demo_mode": DEMO_MODE,
    }


@app.get("/api/history", response_model=ChatHistory)
def get_history(request: Request) -> ChatHistory:
    with database_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT role, content
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (get_session_id(request), MAX_CONTEXT_MESSAGES),
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
    messages = [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]
    return ChatHistory(messages=messages)


@app.post("/api/chat", response_model=ChatReply)
def send_message(body: ChatRequest, request: Request) -> ChatReply:
    session_id = get_session_id(request)
    with chat_lock:
        with database_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT role, content
                    FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (session_id, MAX_CONTEXT_MESSAGES),
                )
                rows = cursor.fetchall()
            finally:
                cursor.close()

        messages = [
            {"role": row["role"], "content": row["content"]}
            for row in reversed(rows)
        ]
        messages.append({"role": "user", "content": body.message})

        try:
            reply = ask_model(messages)
        except RateLimitError as error:
            retry_after = error.response.headers.get("retry-after")
            detail = f"{PROVIDER.title()} rate or usage limit reached."
            if retry_after:
                detail += f" Try again in {retry_after} seconds."
            raise HTTPException(status_code=429, detail=detail) from error
        except AuthenticationError as error:
            logger.warning("%s rejected the configured API key.", PROVIDER.title())
            raise HTTPException(
                status_code=503,
                detail=f"{PROVIDER.title()} rejected the API key. Check its key in .env.local.",
            ) from error
        except APIConnectionError as error:
            logger.warning("Could not connect to %s: %s", PROVIDER.title(), error)
            if PROVIDER == "ollama":
                detail = (
                    f"Cannot reach Ollama at {BASE_URL}. Install and start Ollama, "
                    f"then run `ollama pull {MODEL}`."
                )
            elif PROVIDER == "lmstudio":
                detail = (
                    f"Cannot reach LM Studio at {BASE_URL}. Load a model and start "
                    "the local server in LM Studio, then retry."
                )
            else:
                detail = (
                    f"Could not connect to {PROVIDER.title()}. "
                    "Check your internet connection and provider settings."
                )
            raise HTTPException(
                status_code=502,
                detail=detail,
            ) from error
        except APIError as error:
            logger.exception("%s API request failed.", PROVIDER.title())
            if PROVIDER == "ollama" and isinstance(error, APIStatusError):
                if error.status_code == 404:
                    detail = (
                        f"Ollama could not find model '{MODEL}'. "
                        f"Run `ollama pull {MODEL}` and retry."
                    )
                    raise HTTPException(status_code=503, detail=detail) from error
            raise HTTPException(
                status_code=502,
                detail=f"{PROVIDER.title()} could not complete the request. Check the server log for details.",
            ) from error
        except RuntimeError as error:
            logger.error(
                "%s chat configuration/response error: %s",
                PROVIDER.title(),
                error,
            )
            raise HTTPException(status_code=503, detail=str(error)) from error

        with database_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.executemany(
                    """
                    INSERT INTO chat_messages (session_id, role, content)
                    VALUES (%s, %s, %s)
                    """,
                    [
                        (session_id, "user", body.message),
                        (session_id, "assistant", reply),
                    ],
                )
            finally:
                cursor.close()

    return ChatReply(reply=reply)


@app.post("/api/clear")
def clear_history(request: Request) -> dict[str, str]:
    with database_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM chat_messages WHERE session_id = %s",
                (get_session_id(request),),
            )
        finally:
            cursor.close()
    return {"status": "cleared"}


app.mount("/", StaticFiles(directory=FRONTEND), name="frontend")
