import time
from bs4 import BeautifulSoup
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    date_times = []

    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "ul.child-event-dates-list button")
    except NoSuchElementException:
        buttons = []

    if not buttons:
        # Fallback: extract single datetime only
        try:
            datetime_span = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "span.date-info__full-datetime"))
            )
            return datetime_span.text.strip()
        except Exception as e:
            print(f"Could not locate any datetime: {e}")
            return ""

    for i in range(len(buttons)):
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, "ul.child-event-dates-list button")
            button = buttons[i]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            button.click()
            time.sleep(1)

            datetime_span = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "span.date-info__full-datetime"))
            )
            date_times.append(datetime_span.text.strip())

        except Exception as e:
            print(f"Error on button {i}: {e}")
            continue

    return "\\n".join(date_times)


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
        event_intro = clean_text(extract_text_or_none(soup.select_one("p.summary > strong")))

        ticket_cost_el = soup.select_one('div[data-testid="panel-info"]')
        if not ticket_cost_el:
            ticket_cost_el = soup.select_one('span.CondensedConversionBar-module__priceTag___3AnIu')
        ticket_cost = clean_text(ticket_cost_el.get_text()) if ticket_cost_el else "Free"
        print(ticket_cost)

        full_address = ""
        address_container = soup.select_one('div.location-info__address')
        if address_container:
            map_toggle = address_container.select_one('div.map-button-toggle')
            if map_toggle:
                map_toggle.decompose()
            full_address = clean_text(address_container.get_text())

        event_description_el = soup.select_one("div.eds-text--left")
        event_description = clean_text(event_description_el.get_text()) if event_description_el else ""

        event_date_times = extract_all_event_date_times(driver=chromedriver)

        # Format output string as single line with \n separators
        lines = []

        if event_title:
            lines.append(f"Title: {event_title}")
        else:
            return None

        if event_intro:
            lines.append(f"Short Description: {event_intro}")

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