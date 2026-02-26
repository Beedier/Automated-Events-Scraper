"""
llama.cpp_ai/generate_content.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generates structured event content using a local llama.cpp server.

T4 GPU (16GB VRAM) limits with Qwen2.5-7B Q4_K_M (~4.5GB model):
  - ~11GB remaining for KV cache
  - Safe context window: 8192 tokens (--ctx-size 8192 on server)
  - Max output tokens: 2048 (enough for any EventOutput JSON)

Start the server with:
    llama-server -m models/qwen2.5-7b-instruct.gguf \
        --port 8080 \
        --ctx-size 8192 \
        --n-gpu-layers 99
"""

from __future__ import annotations

import logging

from gemini_ai import SYSTEM_INSTRUCTION, EventOutput
from structured_llm import StructuredLLM

logger = logging.getLogger(__name__)

# Output token budget — how many tokens the model may generate.
# 4096 is comfortably enough for a full EventOutput JSON on a T4.
# The remaining context budget (8192 - 4096 = 4096) is available for the prompt.
MAX_OUTPUT_TOKENS = 4096


def generate_event_content_by_llama_cpp_ai(prompt: str, server_url: str) -> EventOutput:
    """Extract structured event data from unstructured text.

    Args:
        prompt: Raw text to extract event data from. Keep under ~6000 tokens
                (~24000 chars) to stay within the T4 context budget.
        server_url: Running llama.cpp server, e.g. "http://localhost:8080".

    Returns:
        Validated EventOutput instance.

    Raises:
        LlamaCppClientError: If the server is unreachable.
        ValidationError: If the output fails schema validation.
    """
    if len(prompt) > 24000:
        logger.warning(
            "Prompt is %d chars — may exceed T4 context budget. "
            "Consider truncating event.web_content before passing.",
            len(prompt),
        )

    llm = StructuredLLM(server_url=server_url, system_prompt=SYSTEM_INSTRUCTION)

    try:
        return llm.generate(model=EventOutput, prompt=prompt, max_tokens=MAX_OUTPUT_TOKENS)
    finally:
        llm.close()
