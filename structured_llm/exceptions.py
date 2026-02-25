"""
structured_llm.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~

Custom exception hierarchy for structured-llm.

We fail fast — no silent fallbacks, no retries.
Every exception has a clear message telling you exactly what went wrong.
"""


class StructuredLLMError(Exception):
    """Base class for all structured-llm errors.

    All exceptions raised by this library inherit from this class,
    so you can catch everything with ``except StructuredLLMError``.
    """


class GrammarGenerationError(StructuredLLMError):
    """Raised when GBNF grammar cannot be generated from the Pydantic model.

    This usually means the model contains a field type we don't support yet
    (e.g. raw ``Any``, complex generics without concrete types, etc.).
    """


class LlamaCppClientError(StructuredLLMError):
    """Raised when the HTTP call to the llama.cpp server fails.

    Possible causes:
    - Server is not running
    - Wrong server_url
    - Network timeout
    - Server returned a non-200 status code
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ValidationError(StructuredLLMError):
    """Raised when the raw LLM output cannot be validated against the Pydantic model.

    If you see this, grammar enforcement worked (the JSON is syntactically valid)
    but the content somehow bypassed a semantic constraint we couldn't encode
    in GBNF (e.g. a custom Pydantic validator).

    We do NOT retry. Fix the prompt or the model definition.
    """


class ServerConfigurationError(StructuredLLMError):
    """Raised when ``StructuredLLM`` is constructed with invalid configuration.

    For example: empty server_url, unreachable server on startup check, etc.
    """
