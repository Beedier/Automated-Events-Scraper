"""
structured_llm.validator
~~~~~~~~~~~~~~~~~~~~~~~~

Parse and validate the raw LLM output into a typed Pydantic instance.

Even though llama.cpp grammar-constrains the output to be *syntactically*
valid JSON, we still run Pydantic validation to:

1. Deserialise the JSON into the correct Python types (int, float, Enum, etc.)
2. Run any custom Pydantic validators the user defined (e.g. @field_validator)
3. Catch the (extremely rare) edge case where grammar enforcement was bypassed

We do NOT retry.  If validation fails, we raise ``ValidationError`` immediately
with a detailed message so you can debug the prompt.
"""

from __future__ import annotations

import json
import logging
from typing import TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from .exceptions import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OutputValidator:
    """Validates a raw JSON string against a Pydantic model.

    This class is intentionally minimal — it does one thing and does it well.
    """

    def validate(self, raw_text: str, model: type[T]) -> T:
        """Parse *raw_text* as JSON and validate it against *model*.

        Parameters
        ----------
        raw_text:
            The string returned by the LLM (should be valid JSON thanks to grammar).
        model:
            The Pydantic v2 ``BaseModel`` subclass to validate against.

        Returns
        -------
        T
            A fully-validated instance of *model*.

        Raises
        ------
        ValidationError
            If JSON parsing or Pydantic validation fails.
        """
        # Step 1: Parse JSON
        try:
            data = json.loads(raw_text.strip())
        except json.JSONDecodeError as exc:
            # This should never happen if grammar worked correctly,
            # but we handle it defensively.
            raise ValidationError(
                f"LLM output is not valid JSON.\n"
                f"Parse error: {exc}\n"
                f"Raw output (first 500 chars): {raw_text[:500]!r}\n\n"
                "This usually means the grammar didn't fire correctly. "
                "Check that the llama.cpp server accepted the 'grammar' field."
            ) from exc

        logger.debug("Parsed JSON: %r", data)

        # Step 2: Pydantic validation
        try:
            instance = model.model_validate(data)
        except PydanticValidationError as exc:
            raise ValidationError(
                f"LLM output is valid JSON but fails Pydantic validation.\n"
                f"Model: {model.__name__}\n"
                f"Errors:\n{exc}\n\n"
                "This can happen if you have custom @field_validator logic that "
                "GBNF grammar cannot encode.  Consider simplifying your validators "
                "or adding explicit constraints to the prompt."
            ) from exc

        logger.debug("Validation succeeded: %r", instance)
        return instance
