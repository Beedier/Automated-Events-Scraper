from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.common.by import By
from library import extract_text_or_none, clean_text


def extract_event_details_from_bco_ul(ul_block: Tag) -> dict:
    """
    Extracts event metadata from a <ul> block on a BCO.org.uk event page.

    Args:
        ul_block (Tag): BeautifulSoup <ul> element containing event details.

    Returns:
        dict: Dictionary with extracted event metadata.
    """
    data = {}
    for li in ul_block.select("li"):
        span = li.find("span")
        if not span:
            continue

        label_raw = str(li.contents[0]).strip().replace("\xa0", " ").lower().rstrip(":")
        label = label_raw.replace(" ", "_")  # Optional normalization

        value = clean_text(span.get_text())

        if not label or not value:
            continue

        data[label] = value

    return data


def get_event_web_content_from_bco_org(
    event_url: str,
    chromedriver: WebDriver
) -> tuple[str, str, str | None]:
    """
    Loads a BCO.org.uk event detail page, extracts and formats event data.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        tuple[str, str, str | None]: A formatted string with event details, and the detected event category.
    """
    chromedriver.get(event_url)

    # Select evnet summary
    event_summary = chromedriver.find_element(by=By.CSS_SELECTOR, value="div.summary.entry-summary")

    soup = BeautifulSoup(event_summary.get_attribute("innerHTML"), "html.parser")

    # product info column
    product_info_col_el = soup.select_one('div.product_info_col')

    # product event info column
    product_event_info_col_el = soup.select_one('div.product_event_info')

    # Extract core elements
    event_category = None
    event_title = clean_text(extract_text_or_none(product_info_col_el.select_one("h1.product_title.entry-title")))
    event_description = "\n".join(
        clean_text(extract_text_or_none(p)) for p in product_info_col_el.select("p") if extract_text_or_none(p)
    )

    # Parse list-based event metadata
    ul = product_event_info_col_el.select_one("ul")
    raw_details = extract_event_details_from_bco_ul(ul) if ul else {}
    event_details = {k: clean_text(v) for k, v in raw_details.items()}

    # Format additional unknown metadata
    extra_lines = []
    for k, v in event_details.items():
        clean_key = k.replace("_", " ").rstrip("_").title()
        extra_lines.append(f"{clean_key}: {v}")

    # Format final output
    formatted = f"Title: {event_title}"

    # Append extra unknown keys
    if extra_lines:
        formatted += "\n" + "\n".join(extra_lines)

    # Append description last
    formatted += f"\nDescription:\n\t{event_description}"
    return event_title, formatted, event_category
