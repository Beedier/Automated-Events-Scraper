
"""
llama_cpp_ai/generate_content.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generates structured event content using a local llama.cpp server.

Start the server before using:
    llama-server -m models/qwen2.5-7b-instruct.gguf --port 8080
"""

from __future__ import annotations

import logging

from gemini_ai import SYSTEM_INSTRUCTION, EventOutput
from structured_llm import StructuredLLM

logger = logging.getLogger(__name__)


def generate_event_content_by_llama_cpp_ai(prompt: str, server_url: str) -> EventOutput:
    """Extract structured event data from unstructured text.

    Args:
        prompt: Raw text to extract event data from.
        server_url: Running llama.cpp server, e.g. "http://localhost:8080".

    Returns:
        Validated EventOutput instance.

    Raises:
        LlamaCppClientError: If the server is unreachable.
        ValidationError: If the output fails schema validation.
    """
    llm = StructuredLLM(server_url=server_url, system_prompt=SYSTEM_INSTRUCTION)

    try:
        return llm.generate(model=EventOutput, prompt=prompt)
    finally:
        llm.close()
