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
    Loads an Eventbrite event detail page, clicks 'Read more' if present,
    extracts and formats event data from targeted sections.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        str: A formatted string with event details, or None if extraction fails.
    """
    chromedriver.get(event_url)
    time.sleep(3)
    try:
        soup = BeautifulSoup(chromedriver.page_source, "html.parser")

        # Scope extraction to the two main content sections
        event_details_el = soup.select_one("[data-testid='event-details']")
        overview_el = soup.select_one("[data-testid='section-wrapper-overview']")

        # Helper to search within scoped sections first, fallback to full soup
        def scoped_select(selector: str):
            for section in [event_details_el, overview_el]:
                if section:
                    el = section.select_one(selector)
                    if el:
                        return el
            return soup.select_one(selector)

        # --- Title (from full soup, it's usually in the header) ---
        event_title = clean_text(
            extract_text_or_none(soup.select_one("h1[data-testid='event-title']"))
        )

        # --- Ticket cost (conversion bar is outside main sections, always use full soup) ---
        conversion_bar_headline_element = soup.select_one(
            '[data-testid="conversion-bar-headline"] span'
        )
        sales_start_soon_panel_element = soup.select_one(
            '[data-testid="sales-start-soon-panel-label"]'
        )
        if conversion_bar_headline_element:
            ticket_cost = clean_text(conversion_bar_headline_element.get_text())
        elif sales_start_soon_panel_element:
            ticket_cost = clean_text(sales_start_soon_panel_element.get_text())
        else:
            ticket_cost = "FREE"

        # --- Location ---
        location = clean_text(
            extract_text_or_none(scoped_select("a[data-testid='event-venue']"))
        )

        # --- Description (from overview section after Read More click) ---
        if overview_el:
            event_description = clean_text(
                overview_el.get_text(separator=" ", strip=True)
            )
        else:
            event_description = ""

        # --- Date/Time: try scoped sections first, fallback to conversion bar date ---
        event_date_time = clean_text(
            extract_text_or_none(scoped_select("div[data-testid='event-datetime'] span"))
        )
        if not event_date_time:
            event_date_time = clean_text(
                extract_text_or_none(
                    soup.select_one('[data-testid="conversion-bar-date"]')
                )
            )

        # --- Build formatted output ---
        lines = []

        if event_title:
            lines.append(f"Title: {event_title}")
        else:
            return None  # Title is mandatory

        if location:
            lines.append(f"Location: {location}")

        if ticket_cost:
            lines.append(f"Cost: {ticket_cost}")

        if event_date_time:
            lines.append(f"Datetime: {event_date_time.strip()}")

        if event_description:
            lines.append(f"Description: {event_description}")

        formatted = "\\n".join(lines)

        return formatted

    except Exception as e:
        print(f"[Eventbrite Scraper Error] {event_url}: {e}")
        return None
