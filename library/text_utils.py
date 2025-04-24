from bs4 import BeautifulSoup
from typing import Optional

def extract_clean_text(soup: BeautifulSoup) -> Optional[str]:
    """
    Extracts and cleans raw text from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML object.

    Returns:
        Optional[str]: Cleaned text, or None on failure.
    """
    if not isinstance(soup, BeautifulSoup):
        return None

    try:
        raw_text = soup.get_text(separator='\n')
    except (AttributeError, TypeError):
        return None

    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    return '\n'.join(lines) if lines else None
