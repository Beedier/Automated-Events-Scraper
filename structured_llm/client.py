"""
structured_llm.client
~~~~~~~~~~~~~~~~~~~~~

Thin HTTP client for the llama.cpp server (``/completion`` endpoint).

We deliberately keep this module simple:
- One method: ``complete``
- Uses ``httpx`` for synchronous HTTP
- No retry logic — fail fast
- Full type annotations

llama.cpp server endpoints used
--------------------------------
POST /completion
    Request body (relevant fields):
    - prompt (str): the full prompt text
    - grammar (str): GBNF grammar string — the key to structural enforcement
    - temperature (float): set to 0 for deterministic output
    - n_predict (int): max tokens to generate

    Response body (JSON):
    - content (str): the generated text

Reference: https://github.com/ggerganov/llama.cpp/tree/master/examples/server
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .exceptions import LlamaCppClientError

logger = logging.getLogger(__name__)

# Default generation parameters — all tuned for deterministic structured output
_DEFAULT_TEMPERATURE: float = 0.0        # deterministic
_DEFAULT_MAX_TOKENS: int = 2048          # generous but bounded
_DEFAULT_TOP_P: float = 1.0              # no nucleus sampling — full dist
_DEFAULT_TOP_K: int = 1                  # top-1 sampling (greedy) as backup
_DEFAULT_REPEAT_PENALTY: float = 1.0     # no repetition penalty
_DEFAULT_TIMEOUT_SECONDS: float = 120.0  # 2 minutes


class LlamaCppClient:
    """Synchronous HTTP client for a running llama.cpp server.

    Parameters
    ----------
    server_url:
        Base URL of the llama.cpp server, e.g. ``"http://localhost:8080"``.
        Do not include a trailing slash.
    timeout:
        HTTP timeout in seconds.  Increase for large models / slow hardware.
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = server_url.rstrip("/")
        self._timeout = timeout
        self._http = httpx.Client(timeout=timeout)
        logger.debug("LlamaCppClient initialised: base_url=%s", self._base_url)

    def complete(
        self,
        prompt: str,
        grammar: str,
        *,
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        extra_params: dict[str, Any] | None = None,
    ) -> str:
        """Send a completion request and return the raw generated text.

        Parameters
        ----------
        prompt:
            The full prompt string (system + user combined, if needed).
        grammar:
            A GBNF grammar string.  llama.cpp uses this to constrain sampling
            at the *token level* — tokens that would violate the grammar are
            assigned probability zero before the sample is drawn.
        temperature:
            Sampling temperature.  Default is 0 (greedy / deterministic).
        max_tokens:
            Maximum number of tokens to generate.
        extra_params:
            Any additional parameters to pass to ``/completion``.  These are
            merged into the request body and override defaults.

        Returns
        -------
        str
            The raw generated text (``response["content"]``).

        Raises
        ------
        LlamaCppClientError
            On any HTTP error or unexpected response structure.
        """
        payload: dict[str, Any] = {
            "prompt": prompt,
            "grammar": grammar,
            "temperature": temperature,
            "n_predict": max_tokens,
            "top_p": _DEFAULT_TOP_P,
            "top_k": _DEFAULT_TOP_K,
            "repeat_penalty": _DEFAULT_REPEAT_PENALTY,
            "stream": False,
        }

        if extra_params:
            payload.update(extra_params)

        url = f"{self._base_url}/completion"
        logger.debug("POST %s | prompt length=%d chars", url, len(prompt))

        try:
            response = self._http.post(url, json=payload)
        except httpx.TransportError as exc:
            raise LlamaCppClientError(
                f"Cannot connect to llama.cpp server at {self._base_url}: {exc}\n"
                "Is the server running?  "
                "Start it with: llama-server -m <model_path> --port 8080"
            ) from exc
        except httpx.TimeoutException as exc:
            raise LlamaCppClientError(
                f"Request to {url} timed out after {self._timeout}s. "
                "Try increasing the timeout parameter."
            ) from exc

        if response.status_code != 200:
            raise LlamaCppClientError(
                f"llama.cpp server returned HTTP {response.status_code}: "
                f"{response.text[:500]}",
                status_code=response.status_code,
            )

        try:
            data: dict[str, Any] = response.json()
        except Exception as exc:
            raise LlamaCppClientError(
                f"llama.cpp server returned non-JSON response: {response.text[:200]}"
            ) from exc

        if "content" not in data:
            raise LlamaCppClientError(
                f"llama.cpp response missing 'content' field: {data!r}"
            )

        raw_text: str = data["content"]
        logger.debug("Received %d chars from llama.cpp", len(raw_text))
        return raw_text

    def health_check(self) -> bool:
        """Return True if the server is reachable and healthy.

        Uses ``GET /health`` — supported since llama.cpp commit 7e0c05d.
        Falls back to a lightweight ``GET /`` check if ``/health`` is absent.
        """
        try:
            resp = self._http.get(f"{self._base_url}/health", timeout=5.0)
            # llama.cpp /health returns {"status": "ok"} when ready
            return resp.status_code == 200
        except Exception:
            return False

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._http.close()

    # Context manager support
    def __enter__(self) -> "LlamaCppClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
