from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import extract_text_or_none, clean_text


def extract_event_details_from_list(ul_block: Tag) -> dict:
    """
    Extracts event metadata from a <ul> block with RIBA's event info structure.

    Args:
        ul_block (Tag): BeautifulSoup <ul> element containing the event list.

    Returns:
        dict: Dictionary with keys: date, place, contact, cost.
    """
    data = {
        "date": None,
        "place": None,
        "contact": None,
        "cost": None,
    }

    for item in ul_block.select("li.call-to-action-hero__list-item"):
        icon = item.select_one("span.call-to-action-hero__list-icon")
        text = extract_text_or_none(item.select_one("span.call-to-action-hero__list-text"))
        if not icon or not text:
            continue

        icon_text = icon.text.strip()

        match icon_text:
            case "today":
                data["date"] = text
            case "place":
                data["place"] = text
            case "call":
                data["contact"] = text
            case "receipt":
                data["cost"] = text

    return data


def get_event_web_content_from_riba(
    event_url: str,
    chromedriver: WebDriver
) -> str | None:
    """
    Loads a RIBA event detail page, extracts and formats event data.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        str: A formatted string with event details, and the detected event category.
        None: If any error occurs during scraping or parsing.
    """
    chromedriver.get(event_url)

    # Accept cookie dialog if it appears
    try:
        accept_cookies_button = WebDriverWait(chromedriver, 2).until(
            ec.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        accept_cookies_button.click()
    except TimeoutException:
        pass
    try:
        soup = BeautifulSoup(chromedriver.page_source, "html.parser")

        # Extract core elements
        event_type = clean_text(extract_text_or_none(soup.select_one("span.call-to-action-hero__tag")))
        event_title = clean_text(extract_text_or_none(soup.select_one("h1.call-to-action-hero__title")))
        event_intro = clean_text(extract_text_or_none(soup.select_one("p.call-to-action-hero__intro")))
        event_description = extract_text_or_none(soup.select_one("article.rich-text"))

        # Parse list-based event metadata
        ul = soup.select_one("ul.call-to-action-hero__list")
        raw_details = extract_event_details_from_list(ul) if ul else {}
        event_details = {k: clean_text(v) for k, v in raw_details.items()}

        # Format output string
        formatted = f"""\
Title: {event_title}
Event Type: {event_type}
Intro: {event_intro}
Date: {event_details.get("date")}
Place: {event_details.get("place")}
Contact: {event_details.get("contact")}
Cost: {event_details.get("cost")}
Description: {event_description}"""

        return formatted
    except Exception as e:
        print(e)
        return None
