from bs4 import BeautifulSoup
from selenium.webdriver.ie.webdriver import WebDriver
from library import extract_text_or_none, clean_text


def get_event_web_content_from_nla_london(
    event_url: str,
    chromedriver: WebDriver
) -> str:
    """
    Loads a NLA London event detail page, extracts and formats event data.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        str: A formatted string with event details.
    """
    chromedriver.get(event_url)
    soup = BeautifulSoup(chromedriver.page_source, "html.parser")

    # Extract core elements safely
    event_type = clean_text(extract_text_or_none(soup.select_one("p.is-bold.is-uppercase.mb8")))
    event_title = clean_text(extract_text_or_none(soup.select_one("h1.inner-big-title.is-bold.is-uppercase")))
    event_date_time = clean_text(soup.select_one("p.lead.mb8").get_text())

    event_description = clean_text(soup.select_one("div.cell.tablet-8.large-9").get_text()) if soup.select_one("div.cell.tablet-8.large-9") else None
    event_details = clean_text(soup.select_one("div.cell.tablet-4.large-3").get_text()) if soup.select_one("div.cell.tablet-4.large-3") else None

    formatted = f"""
Title: {event_title}
Event Type: {event_type}
Date and Time: {event_date_time}
Event Details: 
{event_details}

Description: 
{event_description}
""".strip()

    return formatted
