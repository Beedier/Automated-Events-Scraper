"""
structured_llm.api
~~~~~~~~~~~~~~~~~~

The user-facing ``StructuredLLM`` class.

This is the only class most users will ever import.  It wires together the
three internal layers:

    ┌──────────────────────────────────────┐
    │             StructuredLLM            │  ← you are here
    ├──────────────┬───────────────────────┤
    │ GBNFGrammar  │  LlamaCppClient       │
    │ Generator    │  (HTTP to server)     │
    ├──────────────┴───────────────────────┤
    │         OutputValidator              │
    └──────────────────────────────────────┘

Usage
-----
::

    from structured_llm import StructuredLLM
    from pydantic import BaseModel

    class MyOutput(BaseModel):
        name: str
        score: int

    llm = StructuredLLM(server_url="http://localhost:8080")
    result = llm.generate(model=MyOutput, prompt="...")
    print(result.name, result.score)
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from .client import LlamaCppClient
from .exceptions import ServerConfigurationError, StructuredLLMError
from .grammar import GBNFGrammarGenerator
from .validator import OutputValidator

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Default system prompt — instructs the model to output only JSON.
# The grammar enforcement is the real guarantee; this just helps the model
# skip any preamble text.
_DEFAULT_SYSTEM_PROMPT = (
    "You are a structured data extraction assistant. "
    "Respond ONLY with a valid JSON object matching the requested schema. "
    "Do not include any explanation, markdown, or surrounding text."
)


class StructuredLLM:
    """Generate deterministic, schema-valid structured output from a local LLM.

    This class is the single entry point for the library.

    Parameters
    ----------
    server_url:
        URL of the running llama.cpp HTTP server.
        Example: ``"http://localhost:8080"``
    model_path:
        (Optional) Path to the GGUF model file.  Not used for generation —
        llama.cpp is already loaded with the model when the server starts.
        Stored for informational/logging purposes only.
    timeout:
        HTTP timeout in seconds for generation requests.  Large models on slow
        hardware may need more than the default 120 seconds.
    verify_server_on_init:
        If True (default), call ``GET /health`` during ``__init__`` and raise
        ``ServerConfigurationError`` if the server is unreachable.  Set to
        False to skip the check (e.g. in unit tests with mocked HTTP).
    system_prompt:
        Override the default system prompt injected before every generation.

    Raises
    ------
    ServerConfigurationError
        If ``server_url`` is empty, or if ``verify_server_on_init=True`` and
        the server is not reachable.
    """

    def __init__(
        self,
        server_url: str,
        *,
        model_path: str | None = None,
        timeout: float = 120.0,
        verify_server_on_init: bool = True,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        if not server_url:
            raise ServerConfigurationError("server_url must not be empty.")

        self._model_path = model_path
        self._system_prompt = system_prompt

        # Initialise internal components
        self._client = LlamaCppClient(server_url=server_url, timeout=timeout)
        self._grammar_gen = GBNFGrammarGenerator()
        self._validator = OutputValidator()

        if verify_server_on_init:
            if not self._client.health_check():
                raise ServerConfigurationError(
                    f"Cannot reach llama.cpp server at {server_url}.\n"
                    "Please start the server before constructing StructuredLLM.\n"
                    "Example command:\n"
                    "  llama-server -m models/your-model.gguf --port 8080"
                )
            logger.info("llama.cpp server health check passed: %s", server_url)

    def generate(
        self,
        model: type[T],
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        extra_llm_params: dict[str, Any] | None = None,
    ) -> T:
        """Generate a structured response validated against *model*.

        Parameters
        ----------
        model:
            A Pydantic v2 ``BaseModel`` subclass.  The JSON Schema of this
            model is compiled into a GBNF grammar and enforced at token level.
        prompt:
            The user's prompt / input text.  The system prompt is prepended
            automatically (override via ``system_prompt`` parameter).
        system_prompt:
            Override the instance-level system prompt for this call only.
        max_tokens:
            Maximum number of tokens to generate.
        extra_llm_params:
            Extra parameters forwarded directly to the ``/completion`` endpoint.
            Useful for ``seed``, ``stop``, etc.

        Returns
        -------
        T
            A validated instance of *model*.

        Raises
        ------
        GrammarGenerationError
            If the grammar cannot be compiled from *model*.
        LlamaCppClientError
            If the HTTP call to the server fails.
        ValidationError
            If the LLM output is structurally invalid (should be extremely rare
            with grammar enforcement active).
        """
        logger.info("generate() called: model=%s", model.__name__)

        # 1. Compile grammar from Pydantic model
        grammar = self._grammar_gen.generate(model)
        logger.debug("Grammar compiled (%d chars)", len(grammar))

        # 2. Build the full prompt
        sys_prompt = system_prompt if system_prompt is not None else self._system_prompt
        full_prompt = self._build_prompt(sys_prompt, prompt)

        # 3. Call llama.cpp server (grammar-constrained)
        raw_output = self._client.complete(
            prompt=full_prompt,
            grammar=grammar,
            max_tokens=max_tokens,
            extra_params=extra_llm_params,
        )

        logger.debug("Raw LLM output: %r", raw_output[:300])

        # 4. Validate and return typed instance
        return self._validator.validate(raw_output, model)

    def get_grammar(self, model: type[BaseModel]) -> str:
        """Return the GBNF grammar string for *model* without calling the LLM.

        Useful for debugging and inspecting what grammar will be sent.
        """
        return self._grammar_gen.generate(model)

    def close(self) -> None:
        """Release HTTP resources.  Call when done to avoid connection leaks."""
        self._client.close()

    def __enter__(self) -> "StructuredLLM":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(system_prompt: str, user_prompt: str) -> str:
        """Combine system and user prompts into a single string.

        llama.cpp ``/completion`` takes a raw prompt string, so we use a
        simple but effective format.  If you're using a model with a specific
        chat template (e.g. ChatML, Llama-3 instruct), consider overriding
        this via ``system_prompt`` or pre-formatting your prompt externally.
        """
        return (
            f"<|system|>\n{system_prompt}\n"
            f"<|user|>\n{user_prompt}\n"
            f"<|assistant|>\n"
        )
