from google import genai
from .create_prompt import SYSTEM_INSTRUCTION
from pydantic import BaseModel, model_validator, Field
from typing import List, Optional, Any
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


def generate_text_with_gemini(api_key: str, prompt: str):
    """
    Generates text using the Gemini API based on input text and a prompt.

    Args:
        api_key (str): Gemini api key.
        prompt (str): The prompt to guide the text generation.

    Returns:
        str: The generated text, or None if an error occurs.
    """
    try:
        # Configure the Gemini API with the API key.
        client = genai.Client(api_key=api_key)

        # Generate content using the model.
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=EventOutput,
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        # Return the generated text.
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
