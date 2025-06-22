import re

def extract_text_or_none(element):
    return element.get_text(strip=True) if element else None

def clean_text(text: str | None) -> str | None:
    """Cleans text by collapsing whitespace and fixing missing space before capital letters."""
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text)  # collapse all whitespace
    return text.strip()
