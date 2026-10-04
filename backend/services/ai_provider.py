"""AI provider abstraction — OpenAI, Anthropic, Ollama, or none.

The browser never sees the API key. Every AI request goes through this module.
"""
from __future__ import annotations
from typing import Any
import os
import httpx
from fastapi import HTTPException
from ..config import get_settings

settings = get_settings()


async def chat(messages: list[dict], max_tokens: int = 800, temperature: float = 0.7) -> dict:
    """Return { text, tokens_in, tokens_out }."""
    provider = (settings.ai_provider or "none").lower()

    if provider == "none" or not settings.ai_api_key and provider != "ollama":
        raise HTTPException(503, "AI is not configured on this server. Set AI_PROVIDER and AI_API_KEY.")

    if provider == "openai":
        return await _openai(messages, max_tokens, temperature)
    if provider == "anthropic":
        return await _anthropic(messages, max_tokens, temperature)
    if provider == "ollama":
        return await _ollama(messages, max_tokens, temperature)
    raise HTTPException(500, f"Unknown AI provider: {provider}")


async def _openai(messages, max_tokens, temperature):
    base = settings.ai_base_url or "https://api.openai.com/v1"
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {settings.ai_api_key}"},
            json={
                "model": settings.ai_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"OpenAI error: {r.text[:300]}")
    j = r.json()
    return {
        "text": j["choices"][0]["message"]["content"],
        "tokens_in": j.get("usage", {}).get("prompt_tokens", 0),
        "tokens_out": j.get("usage", {}).get("completion_tokens", 0),
    }


async def _anthropic(messages, max_tokens, temperature):
    # Split system message
    system = ""
    rest = []
    for m in messages:
        if m["role"] == "system":
            system += m["content"] + "\n"
        else:
            rest.append(m)

    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ai_api_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.ai_model or "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system.strip() or None,
                "messages": rest,
            },
        )
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"Anthropic error: {r.text[:300]}")
    j = r.json()
    return {
        "text": j["content"][0]["text"],
        "tokens_in": j.get("usage", {}).get("input_tokens", 0),
        "tokens_out": j.get("usage", {}).get("output_tokens", 0),
    }


async def _ollama(messages, max_tokens, temperature):
    base = settings.ai_base_url or "http://localhost:11434"
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(
            f"{base}/api/chat",
            json={
                "model": settings.ai_model or "llama3.1",
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
        )
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"Ollama error: {r.text[:300]}")
    j = r.json()
    return {
        "text": j.get("message", {}).get("content", ""),
        "tokens_in": j.get("prompt_eval_count", 0),
        "tokens_out": j.get("eval_count", 0),
    }