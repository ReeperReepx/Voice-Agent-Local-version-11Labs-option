"""Qwen2.5-72B Instruct runtime.

Connects to local Qwen via vLLM (OpenAI-compatible API) or Ollama.
Defaults to 72B as per infrastructure spec. Set LLM_MODEL=qwen2.5:7b for smaller GPU.
Thin wrapper — no model code changes.
"""

import os
from pathlib import Path
from typing import Optional

import httpx

LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434")

TEMPLATES_DIR = Path(__file__).parent / "prompt_templates"


def load_template(name: str) -> str:
    """Load a prompt template from the templates directory."""
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {name}")
    return path.read_text().strip()


def build_system_prompt(
    state: str,
    destination_country: str,
    explanation_mode: bool = False,
) -> str:
    """Build the system prompt for the LLM based on current state."""
    base = load_template("base_system.txt")
    tone = load_template("examiner_tone.txt")

    if explanation_mode:
        mode = load_template("explanation_mode.txt")
    else:
        mode = ""

    return f"{base}\n\n{tone}\n\nCurrent interview state: {state}\nDestination country: {destination_country}\n{mode}".strip()


def generate_response(
    system_prompt: str,
    conversation_history: list[dict],
    user_message: str,
    language: str = "en",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate a response from the LLM.

    Args:
        system_prompt: The system prompt
        conversation_history: List of {"role": "user"|"assistant", "content": str}
        user_message: The latest user message
        language: Output language ("en" or "hi")
        max_tokens: Max response tokens
        temperature: Sampling temperature

    Returns:
        The generated text response.
    """
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    if LLM_BACKEND == "vllm":
        return _call_vllm(messages, max_tokens, temperature)
    else:
        return _call_ollama(messages, max_tokens, temperature)


def _call_ollama(
    messages: list[dict],
    max_tokens: int,
    temperature: float,
) -> str:
    """Call Ollama API."""
    url = f"{LLM_API_URL}/api/chat"
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    response = httpx.post(url, json=payload, timeout=120.0)
    response.raise_for_status()
    return response.json()["message"]["content"]


def _call_vllm(
    messages: list[dict],
    max_tokens: int,
    temperature: float,
) -> str:
    """Call vLLM OpenAI-compatible API."""
    url = f"{LLM_API_URL}/v1/chat/completions"
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = httpx.post(url, json=payload, timeout=120.0)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def check_health() -> bool:
    """Check if the LLM backend is reachable."""
    try:
        if LLM_BACKEND == "vllm":
            r = httpx.get(f"{LLM_API_URL}/v1/models", timeout=5.0)
        else:
            r = httpx.get(f"{LLM_API_URL}/api/tags", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False
