import time
from bs4 import BeautifulSoup
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import extract_text_or_none, clean_text


def extract_all_event_date_times(driver) -> str:
    """
    Clicks each event date button (if available) and extracts the corresponding full datetime string.
    If no list is found, extracts a single visible datetime.

    Returns:
        str: Newline-separated datetime strings.
    """
    try:
        time_tag = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, "time.start-date-and-location__date"))
        )
        return time_tag.text.strip()
    except Exception as e:
        print(f"Could not locate any datetime: {e}")
        return ""


def get_event_web_content_from_event_bright(
    event_url: str,
    chromedriver: WebDriver
) -> str | None:
    """
    Loads an Eventbrite event detail page, extracts and formats event data.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        str: A formatted string with event details.
    """
    chromedriver.get(event_url)

    try:
        # wait to load whole page properly
        time.sleep(5)

        soup = BeautifulSoup(chromedriver.page_source, "html.parser")

        event_title = clean_text(extract_text_or_none(soup.select_one("h1.event-title")))
        event_summary = clean_text(extract_text_or_none(soup.select_one("div.summary")))
        event_category = clean_text(extract_text_or_none(soup.select_one("div[data-testid='category-badge']")))

        ticket_cost = "Free"
        # 1️⃣ Try top price selector
        el = soup.select_one(
            'div[data-testid="condensed-conversion-bar"] span.CondensedConversionBar-module__priceTag___3AnIu'
        )
        if el:
            ticket_cost = clean_text(el.get_text())
        else:
            # 2️⃣ Fallback to panel-info price
            el = soup.select_one("div.check-availability-btn__panel-info")
            if el:
                # take only the first text part (the cost), not message
                price = el.get_text().split("\n")[0]
                ticket_cost = clean_text(price)

        full_address = clean_text(extract_text_or_none(soup.select_one('div.Location-module__addressWrapper___1mn7I')))

        event_description_el = soup.select_one("div.eds-text--left")
        event_description = clean_text(event_description_el.get_text()) if event_description_el else ""

        event_date_times = extract_all_event_date_times(driver=chromedriver)

        # Format output string as single line with \n separators
        lines = []

        if event_title:
            lines.append(f"Title: {event_title}")
        else:
            return None

        if event_summary:
            lines.append(f"Summary: {event_summary}")

        if event_category:
            lines.append(event_category)

        if full_address:
            lines.append(f"Location: {full_address}")

        if ticket_cost:
            lines.append(f"Cost: {ticket_cost}")

        if event_date_times:
            lines.append(f"Dates: {event_date_times.strip()}")

        if event_description:
            lines.append(f"Description: {event_description}")

        formatted = "\\n".join(lines)

        return formatted

    except Exception as e:
        print(e)
        return None