"""Helpers for generating structured event content using Gemini.

This module provides a single, well-documented public function
`generate_event_content` that calls the Gemini API and returns a
validated `EventOutput` Pydantic model. Errors from the API or
validation are surfaced as a `GeminiGenerationError` exception and
logged.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from google import genai
from google.genai import types, errors as genai_errors
from pydantic import BaseModel, Field, model_validator, ValidationError

from .create_prompt import SYSTEM_INSTRUCTION
from dbcore.enums import EventCategoryEnum

logger = logging.getLogger(__name__)


class GeminiGenerationError(Exception):
    """Raised when content generation or schema validation fails.

    Wrapping lower-level exceptions in a domain-specific exception makes
    error handling by callers clearer and easier to test.
    """


class GeminiRateLimitError(Exception):
    """Raised when the Gemini API returns a 429 rate-limit error.

    This exception includes the retry delay (in seconds) extracted from the
    API response, allowing callers to sleep and retry intelligently.
    """

    def __init__(self, message: str, retry_after_seconds: float = None):
        """Initialize the rate limit error.

        Args:
            message: Human-readable error message.
            retry_after_seconds: Recommended delay before retrying, in seconds.
                Optional; extracted from API response if available.
        """
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class EventOutput(BaseModel):
    """Pydantic model describing the structured JSON we expect from Gemini.

    Fields mirror the target schema for events. Use `model_validator`
    to coerce/replace missing values with sensible defaults after
    validation.
    """

    Title: Optional[str]
    Dates: Optional[str]
    IndexIntro: Optional[str]
    Intro: Optional[str]
    Content: Optional[str]
    DateOrder: Optional[str]
    Location: Optional[str]
    Cost: Optional[str]
    Categories: List[EventCategoryEnum] = Field(default_factory=list)

    @model_validator(mode="after")
    def _set_defaults(self):
        """Ensure fields have reasonable defaults when omitted.

        This runs after model construction so we can rely on the parsed
        values and then mutate them if necessary.
        """
        if self.Categories is None:
            self.Categories = []
        if self.Dates is None:
            self.Dates = "Date not specified"
        return self


def generate_event_content(api_key: str, prompt: str, *, model: str = "gemini-2.5-flash") -> EventOutput:
    """Generate structured event content from Gemini and validate it.

    Args:
        api_key: Gemini API key.
        prompt: A prompt string guiding the model to produce the expected JSON.
        model: Optional model name override (defaults to ``gemini-2.5-flash``).

    Returns:
        An instance of ``EventOutput`` containing validated event data.

    Raises:
        GeminiGenerationError: If the API call fails or returned JSON
            cannot be validated against ``EventOutput``.
    """

    if not api_key:
        raise GeminiGenerationError("api_key must be provided")

    client = genai.Client(api_key=api_key)

    try:
        # Request JSON output using the SDK's content generator.
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EventOutput,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )

        # The SDK may return different response shapes depending on
        # version and configuration. Normalize by extracting the
        # first nested object or JSON string that matches our model.
        if hasattr(response, "to_json_dict"):
            raw = response.to_json_dict()
        else:
            # Fallback: try candidates attribute from older SDK shapes.
            raw = None
            if getattr(response, "candidates", None):
                raw = getattr(response.candidates[0], "content", None)

        def _find_model_payload(obj):
            """Recursively search `obj` for the first dict that contains
            one or more keys from `EventOutput` or for a JSON string
            that can be parsed into such a dict.
            """
            model_keys = set(EventOutput.model_fields.keys())

            # Direct match
            if isinstance(obj, dict):
                if model_keys & obj.keys():
                    return obj
            if isinstance(obj, str):
                s = obj.strip()
                if s.startswith("{") or s.startswith("["):
                    try:
                        parsed = json.loads(s)
                        return _find_model_payload(parsed)
                    except json.JSONDecodeError:
                        return None

            # Recurse into dicts and lists
            if isinstance(obj, dict):
                for v in obj.values():
                    found = _find_model_payload(v)
                    if found is not None:
                        return found
            elif isinstance(obj, list):
                for item in obj:
                    found = _find_model_payload(item)
                    if found is not None:
                        return found

            return None

        payload = _find_model_payload(raw)
        if payload is None:
            # As a last resort, if raw itself is a dict/list/string that
            # can be treated as JSON for the model, try parsing it.
            if isinstance(raw, (dict, list)):
                payload = raw
            elif isinstance(raw, str):
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    payload = None

        if payload is None:
            raise GeminiGenerationError("Could not extract model JSON from Gemini response")

        # Validate and coerce into our Pydantic model
        try:
            validated = EventOutput.model_validate(payload)
            return validated
        except ValidationError as ve:
            # Catch validation errors and wrap them so callers get a
            # consistent exception type. Log full traceback.
            logger.exception("Schema validation failed for Gemini response")
            raise GeminiGenerationError(f"Response validation error: {ve}") from ve

    except GeminiGenerationError:
        # Re-raise our domain exception unchanged
        raise
    except genai_errors.ClientError as ce:
        # Handle rate limits and quota errors intelligently.
        # The API returns 429 RESOURCE_EXHAUSTED when quota is exceeded.
        if getattr(ce, "status_code", None) == 429 or str(ce).startswith("429"):
            # Extract retry delay from the error response if available.
            retry_seconds = None
            if hasattr(ce, "response") and isinstance(ce.response, dict):
                details = ce.response.get("details", [])
                for detail in details:
                    if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                        retry_delay_str = detail.get("retryDelay", "")
                        # Parse duration like "37.030620552s" to float seconds
                        if retry_delay_str.endswith("s"):
                            try:
                                retry_seconds = float(retry_delay_str[:-1])
                            except ValueError:
                                pass
                        break

            msg = (
                f"Gemini API rate limit exceeded. "
                f"Retry after {retry_seconds} seconds"
                if retry_seconds
                else "Gemini API rate limit exceeded."
            )
            logger.warning(msg)
            raise GeminiRateLimitError(msg, retry_after_seconds=retry_seconds) from ce
        else:
            # Other API errors (auth, not found, etc.)
            logger.exception(f"Gemini API error: {ce}")
            raise GeminiGenerationError(f"Gemini API error: {ce}") from ce
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logger.exception("Unexpected error while calling Gemini API")
        raise GeminiGenerationError("Failed to generate content from Gemini") from exc
