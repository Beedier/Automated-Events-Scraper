def extract_text_or_none(element):
    return element.get_text(strip=True) if element else None

def clean_text(text: str | None) -> str | None:
    """Removes newlines and trims extra spaces from text."""
    return text.replace("\n", " ").strip() if text else None
