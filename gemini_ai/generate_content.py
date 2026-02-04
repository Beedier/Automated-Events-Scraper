from google import genai
from .create_prompt import SYSTEM_INSTRUCTION
from pydantic import BaseModel, model_validator, Field, ValidationError
from typing import List, Optional, Any, Union
from google.genai import types
from dbcore.enums import EventCategoryEnum


# === 1. Define output JSON schema via Pydantic ===
class EventOutput(BaseModel):
    Title: Optional[str]
    Dates: Optional[str]
    IndexIntro: Optional[str]
    Intro: Optional[str]
    Content: Optional[str]
    DateOrder: Optional[str]
    Location: Optional[str]
    Cost: Optional[str]
    Categories: List[EventCategoryEnum] = Field(default_factory=list)

    # Enforce defaults AFTER model creation
    @model_validator(mode="after")
    def enforce_all_or_none(self):
        if self.Categories is None:
            self.Categories = []

        if self.Dates is None:
            self.Dates = "Date not specified"  # Or other placeholder

        return self


def generate_text_with_gemini(api_key: str, prompt: str) -> Union[EventOutput, None]:
    """
    Generates text using the Gemini API based on input text and a prompt.

    Args:
        api_key (str): Gemini api key.
        prompt (str): The prompt to guide the text generation.

    Returns:
        EventOutput if successful, otherwise a string describing the error.
    """
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=EventOutput,
                system_instruction=SYSTEM_INSTRUCTION
            )
        )

        return EventOutput.model_validate(response.to_json_dict())

    except ValidationError as e:
        # Return an error message instead of EventOutput
        return None
