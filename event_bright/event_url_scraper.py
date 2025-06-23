import time
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import build_url_with_params


_paths = [
    "/d/united-kingdom/business--events/architecture/",
    "/d/ireland/business--events/architecture/"
]

def get_event_urls_from_event_bright(
    chromedriver: WebDriver,
    paths: list[str] = None,
    base_page_url: str = "https://www.eventbrite.co.uk/"
) -> dict:
    """
    Scrapes event URLs and image URLs from multiple Eventbrite paths using Selenium.

    Args:
        chromedriver (WebDriver): Selenium WebDriver instance.
        paths (list[str]): List of URL paths to scrape.
        base_page_url (str): Base URL of the Eventbrite site.

    Returns:
        dict: Dictionary containing website name and list of events.
    """
    events_data = {
        "website_name": "event-bright",
        "events": []
    }

    if paths is None:
        paths = _paths

    for path in paths:
        print(f"Scraping: {path}")
        # Load the first page
        page_url = build_url_with_params(
            base_url=base_page_url,
            path=path,
            query_params={"page": 1}
        )
        chromedriver.get(page_url)

        while True:
            time.sleep(5)  # Let content load

            event_cards = chromedriver.find_elements(By.CSS_SELECTOR, "section.horizontal-event-card__column")
            for card in event_cards:
                try:
                    url = card.find_element(By.CLASS_NAME, "event-card-link").get_attribute("href")
                    image_url = card.find_element(By.CLASS_NAME, "event-card-image").get_attribute("src")
                    events_data["events"].append({
                        "url": url,
                        "image_url": image_url
                    })
                except NoSuchElementException:
                    continue

            # Try to go to the next page
            try:
                next_button = WebDriverWait(chromedriver, 10).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next Page']"))
                )
                next_button.click()
            except TimeoutException:
                break

    return events_data
