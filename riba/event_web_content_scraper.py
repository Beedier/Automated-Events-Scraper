from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import extract_text_or_none, clean_text


def extract_event_details_from_list(div_block: Tag) -> dict:
    """
    Extracts event metadata from a <div> block with RIBA's event info structure.

    Args:
        div_block (Tag): BeautifulSoup <div> element containing the event list.

    Returns:
        dict: Dictionary with keys: date, place, contact, cost.
    """
    data = {
        "date": None,
        "price": None,
        "time": None,
        "organized_by": None,
        "location": None
    }

    for item in div_block.select("div.detail-page-banner__bite"):
        detail_label = extract_text_or_none(item.select_one("div.detail-page-banner__bite-label"))
        detail_info = extract_text_or_none(item.select_one("div.detail-page-banner__bite-value"))

        if detail_label is not None:
            match detail_label.lower():
                case "date":
                    data["date"] = detail_info
                case "price":
                    data["price"] = detail_info
                case "time":
                    data["time"] = detail_info
                case "organised by":
                    data["organized_by"] = detail_info
                case "location":
                    data["location"] = detail_info

    return data

def extract_tabbed_content(html: BeautifulSoup):
    buttons = html.select(".tabbed-content-block__tab")
    contents = html.select(".tabbed-content-block__content")
    result = []

    for i, btn in enumerate(buttons):
        title_text = extract_text_or_none(btn.select_one(".tabbed-content-block__tab-name"))
        content_text = extract_text_or_none(contents[i].select_one(".rich-text")) if i < len(contents) else None
        if title_text and content_text:
            result.append(f"{title_text}: {content_text}")

    return result


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
        event_title = clean_text(extract_text_or_none(soup.select_one("h1.detail-page-banner__text-title")))
        event_intro = clean_text(extract_text_or_none(soup.select_one("div.tabbed-content-block__description.body-text")))
        event_description_items = extract_tabbed_content(html=soup)

        # Parse list-based event metadata
        div_element = soup.select_one("div.detail-page-banner__info")
        raw_details = extract_event_details_from_list(div_element) if div_element else {}
        event_details = {k: clean_text(v) for k, v in raw_details.items()}

        # Format output string as single line with \n separators
        lines = []

        if event_title:
            lines.append(f"Title: {event_title}")
        else:
            return None

        if event_intro:
            lines.append(f"Short Description: {event_intro}")
        if event_details.get('date'):
            lines.append(f"Date: {event_details['date']}")
        if event_details.get('time'):
            lines.append(f"Time: {event_details['time']}")
        if event_details.get('price'):
            lines.append(f"Price: {event_details['price']}")
        if event_details.get('organized_by'):
            lines.append(f"Organized by: {event_details['organized_by']}")
        if event_details.get("location"):
            lines.append(f"Location: {event_details['location']}")

        # combined 2 list
        lines.extend(event_description_items)

        formatted = "\\n".join(lines)

        return formatted
    except Exception as e:
        print(e)
        return None
