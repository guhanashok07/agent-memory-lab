"""Thin client for the local Ollama server.

Standard library only, so the harness has no runtime dependencies to drift.
"""

import json
import os
import time
import urllib.request


def _host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _call(path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{_host()}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)


def chat(model: dict, messages: list[dict], *, seed: int, schema: dict | None = None) -> dict:
    """One non-streaming chat call. Returns the full request alongside the reply,
    so every call can be logged and replayed exactly."""
    body = {
        "model": model["model"],
        "messages": messages,
        "stream": False,
        "options": {"seed": seed, "temperature": model["temperature"]},
    }
    if "think" in model:
        body["think"] = model["think"]
    if schema is not None:
        # Ollama constrains decoding to this JSON schema, so replies always parse.
        body["format"] = schema
    started = time.time()
    reply = _call("/api/chat", body)
    return {
        "request": body,
        "content": reply["message"]["content"],
        "seconds": round(time.time() - started, 2),
    }


def chat_json(model: dict, messages: list[dict], *, seed: int, schema: dict) -> tuple[dict, dict]:
    call = chat(model, messages, seed=seed, schema=schema)
    return json.loads(call["content"]), call


def verify_pins(*models: dict) -> None:
    """Refuse to run if a local model is not the exact build the config pins.

    A tag like qwen3:8b can be re-pushed upstream; the digest cannot."""
    installed = {m["name"]: m["digest"] for m in _call("/api/tags")["models"]}
    for m in models:
        digest = installed.get(m["model"])
        if digest is None:
            raise SystemExit(f"{m['model']} is not installed. Run: ollama pull {m['model']}")
        if not digest.startswith(m["digest"]):
            raise SystemExit(
                f"{m['model']} is digest {digest[:12]}, config pins {m['digest']}. "
                "Results would not be comparable."
            )
