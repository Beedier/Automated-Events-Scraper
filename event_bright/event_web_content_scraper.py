import time
from bs4 import BeautifulSoup
from bs4.element import Tag
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

    return "\n".join(date_times)


def get_event_web_content_from_event_bright(
    event_url: str,
    chromedriver: WebDriver
) -> str:
    """
    Loads an Eventbrite event detail page, extracts and formats event data.

    Args:
        event_url (str): URL of the event page.
        chromedriver (WebDriver): Selenium WebDriver instance.

    Returns:
        str: A formatted string with event details.
    """
    chromedriver.get(event_url)
    soup = BeautifulSoup(chromedriver.page_source, "html.parser")

    event_title = clean_text(extract_text_or_none(soup.select_one("h1.event-title")))
    event_intro = clean_text(extract_text_or_none(soup.select_one("p.summary > strong")))

    ticket_cost_el = soup.select_one('div[data-testid="panel-info"]')
    ticket_cost = clean_text(ticket_cost_el.get_text()) if ticket_cost_el else "Free"

    full_address = "Not found"
    address_container = soup.select_one('div.location-info__address')
    if address_container:
        map_toggle = address_container.select_one('div.map-button-toggle')
        if map_toggle:
            map_toggle.decompose()
        full_address = clean_text(address_container.get_text())

    event_description_el = soup.select_one("div.eds-text--left")
    event_description = clean_text(event_description_el.get_text()) if event_description_el else "No description."

    event_date_times = extract_all_event_date_times(driver=chromedriver)

    return f"""\
Title: {event_title}
Intro: {event_intro}
Dates:
{event_date_times.strip()}

Location: {full_address}
Cost: {ticket_cost}
Description: {event_description}"""