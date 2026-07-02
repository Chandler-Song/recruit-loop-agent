"""
LLM Client — Async HTTPX-based client for OpenAI-compatible chat completions API.

Supports OpenAI, DeepSeek, Qwen (DashScope), Ollama, vLLM, and any
OpenAI-compatible endpoint.  Configuration is read from ``app.core.config.settings``
and can be overridden per-call.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import Settings, settings

logger = logging.getLogger("recruiting_agent.llm")

# ---------------------------------------------------------------------------
# Public data class
# ---------------------------------------------------------------------------


class LLMResponse:
    """Wrapper around a single chat-completion response."""

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        raw: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.content: str = content
        self.model: str = model
        self.usage: Dict[str, int] = usage or {}
        self.raw: Dict[str, Any] = raw or {}

    def json(self) -> Any:
        """Try to parse *content* as JSON; return parsed object or ``None``."""
        try:
            # Strip markdown code fences if present
            text = self.content.strip()
            if text.startswith("```"):
                lines = text.splitlines()
                # Remove first (```lang) and last (```) lines
                lines = [l for l in lines[1:] if l.strip() != "```"]
                text = "\n".join(lines)
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return None


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class LLMClient:
    """
    Async LLM client that calls the ``/chat/completions`` endpoint of any
    OpenAI-compatible API.

    Parameters
    ----------
    api_base_url : str | None
        Base URL of the API (e.g. ``https://api.openai.com/v1``).
        Falls back to ``settings.llm_api_base_url``.
    api_key : str | None
        Bearer token.  Falls back to ``settings.llm_api_key``.
    model : str | None
        Model name.  Falls back to ``settings.llm_model_name``.
    temperature : float | None
        Sampling temperature.  Falls back to ``settings.llm_temperature``.
    max_tokens : int | None
        Max output tokens.  Falls back to ``settings.llm_max_tokens``.
    timeout : float | None
        HTTP timeout in seconds.  Falls back to ``settings.llm_timeout``.
    max_retries : int
        Number of retries on transient HTTP errors (default 2).
    """

    def __init__(
        self,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        max_retries: int = 2,
        _settings: Optional[Settings] = None,
    ) -> None:
        s = _settings or settings
        self.api_base_url: str = (api_base_url or s.llm_api_base_url or "").rstrip("/")
        self.api_key: Optional[str] = api_key or s.llm_api_key
        self.model: str = model or s.llm_model_name
        self.temperature: float = temperature if temperature is not None else s.llm_temperature
        self.max_tokens: int = max_tokens if max_tokens is not None else s.llm_max_tokens
        self.timeout: float = timeout if timeout is not None else s.llm_timeout
        self.max_retries: int = max_retries

    # -- public API ---------------------------------------------------------

    async def chat(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        response_format: Optional[str] = None,
    ) -> LLMResponse:
        """
        Send a chat completion request and return an :class:`LLMResponse`.

        Parameters
        ----------
        user_prompt : str
            The user message.
        system_prompt : str
            The system message prepended to the conversation.
        temperature / max_tokens / model :
            Per-call overrides.
        response_format : str | None
            If ``"json"``, the request asks the model for JSON output.
        """
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload: Dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        data = await self._request_with_retry(payload)

        # Extract content from the OpenAI response shape
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected response structure: {data}") from exc

        return LLMResponse(
            content=content or "",
            model=payload["model"],
            usage=data.get("usage", {}),
            raw=data,
        )

    async def chat_json(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant. Respond with valid JSON only.",
        **kwargs: Any,
    ) -> Any:
        """
        Convenience wrapper: call :meth:`chat` with ``response_format="json"``
        and parse the result.  Returns the parsed Python object, or ``None``
        if parsing fails.
        """
        resp = await self.chat(
            user_prompt,
            system_prompt,
            response_format="json",
            **kwargs,
        )
        parsed = resp.json()
        if parsed is None:
            logger.warning("LLM returned non-JSON content despite json format request")
        return parsed

    # -- internal -----------------------------------------------------------

    async def _request_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST to ``/chat/completions`` with retry on transient errors."""
        url = f"{self.api_base_url}/chat/completions"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 2):  # +2 because first is attempt 1
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.debug(
                        "LLM request attempt %d/%d  model=%s",
                        attempt,
                        self.max_retries + 1,
                        payload.get("model"),
                    )
                    resp = await client.post(url, json=payload, headers=headers)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                wait = min(2 ** attempt, 10)
                logger.warning(
                    "LLM request failed (attempt %d): %s — retrying in %ds",
                    attempt,
                    exc,
                    wait,
                )
                await asyncio.sleep(wait)
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code >= 500:
                    wait = min(2 ** attempt, 10)
                    logger.warning(
                        "LLM server error %d (attempt %d) — retrying in %ds",
                        exc.response.status_code,
                        attempt,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                # 4xx — do not retry
                raise LLMError(
                    f"LLM API returned {exc.response.status_code}: {exc.response.text}"
                ) from exc
            except Exception as exc:
                raise LLMError(f"Unexpected error during LLM call: {exc}") from exc

        raise LLMError(
            f"LLM request failed after {self.max_retries + 1} attempts: {last_exc}"
        )


# ---------------------------------------------------------------------------
# Module-level convenience (singleton-like)
# ---------------------------------------------------------------------------

_default_client: Optional[LLMClient] = None


def get_llm_client(**overrides: Any) -> LLMClient:
    """
    Return a module-level :class:`LLMClient` singleton.

    Pass keyword arguments to create a custom instance instead.
    """
    global _default_client
    if overrides:
        return LLMClient(**overrides)
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class LLMError(Exception):
    """Raised when an LLM API call fails after retries."""
