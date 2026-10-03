"""OpenAI-compatible model client for OpenAI, Ollama, and OpenRouter."""

import os
from collections.abc import Sequence
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv(Path(__file__).with_name(".env.local"), override=True)

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
PROVIDER_URLS = {
    "ollama": "http://127.0.0.1:11434/v1",
    "lmstudio": "http://127.0.0.1:1234/v1",
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}
if PROVIDER not in PROVIDER_URLS:
    raise ValueError(
        "LLM_PROVIDER must be one of: ollama, lmstudio, openai, or openrouter."
    )

MODEL = os.getenv(
    "LLM_MODEL",
    os.getenv(
        "OPENAI_MODEL",
        "llama3.2:3b" if PROVIDER == "ollama" else "gpt-4o-mini",
    ),
)
BASE_URL = os.getenv("LLM_BASE_URL", PROVIDER_URLS[PROVIDER]).rstrip("/")
DEMO_MODE = os.getenv(
    "LLM_DEMO_MODE",
    os.getenv("OPENAI_DEMO_MODE", "false"),
).lower() == "true"


def _api_key() -> str:
    if PROVIDER in {"ollama", "lmstudio"}:
        return "ollama"
    if PROVIDER == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing. Add a real OpenRouter key "
                "to .env.local."
            )
        return api_key

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add a real OpenAI key to .env.local."
        )
    return api_key


def ask_model(messages: Sequence[ChatCompletionMessageParam]) -> str:
    """Send the conversation to the configured OpenAI-compatible provider."""
    if DEMO_MODE:
        latest_message = messages[-1]["content"] if messages else ""
        if not isinstance(latest_message, str):
            latest_message = "[non-text message]"
        return f"Demo reply (no model request): I received: {latest_message}"

    client = OpenAI(
        api_key=_api_key(),
        base_url=f"{BASE_URL}/",
        timeout=120.0 if PROVIDER in {"ollama", "lmstudio"} else 45.0,
        max_retries=0 if PROVIDER in {"ollama", "lmstudio"} else 1,
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=list(messages),
        max_tokens=600,
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError(f"{PROVIDER.title()} returned an empty response.")
    return answer
