"""
structured_llm
~~~~~~~~~~~~~~

Deterministic structured LLM output using llama.cpp with GBNF grammar-constrained decoding.

Quick start::

    from structured_llm import StructuredLLM
    from pydantic import BaseModel

    class EventOutput(BaseModel):
        name: str
        date: str
        location: str

    llm = StructuredLLM(server_url="http://localhost:8080")

    result = llm.generate(
        model=EventOutput,
        prompt="Extract: The Python Summit will be held on March 15 in Berlin.",
    )
    print(result)  # EventOutput(name='Python Summit', date='March 15', location='Berlin')
"""

from .api import StructuredLLM
from .exceptions import (
    GrammarGenerationError,
    LlamaCppClientError,
    ServerConfigurationError,
    StructuredLLMError,
    ValidationError,
)
from .grammar import GBNFGrammarGenerator

__all__ = [
    "StructuredLLM",
    "GBNFGrammarGenerator",
    "StructuredLLMError",
    "GrammarGenerationError",
    "LlamaCppClientError",
    "ServerConfigurationError",
    "ValidationError",
]

__version__ = "0.1.0"
