import time
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import build_url_with_params


def get_event_urls_from_riba(
    chromedriver: WebDriver,
    start_page: int = 1,
    base_page_url: str = "https://www.riba.org/whats-on"
) -> dict:
    """
    Scrapes event URLs and image URLs from RIBA What's On page using Selenium.

    Args:
        chromedriver (WebDriver): Selenium WebDriver instance.
        start_page (int, optional): Starting page number for pagination. Defaults to 1.
        base_page_url (str, optional): Base URL of the RIBA events listing page.

    Returns:
        dict: A dictionary containing website name and list of events with 'url' and 'image_url'.
    """
    events_data = {
        "website_name": "riba",
        "events": []
    }

    current_page = start_page

    # Build and load the first page
    first_page_url = build_url_with_params(
        base_url=base_page_url,
        query_params={"page": current_page}
    )
    chromedriver.get(url=first_page_url)

    # Attempt to click the cookie consent button once
    try:
        accept_cookies_button = WebDriverWait(chromedriver, 10).until(
            ec.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        accept_cookies_button.click()
    except TimeoutException:
        pass  # Cookie dialog not shown or already accepted

    while True:
        # Parse event data from current page
        events = chromedriver.find_elements(By.CSS_SELECTOR, "div.listing-block__cards > div.listing-card")
        for event in events:
            try:
                _event = event.find_element(By.CSS_SELECTOR, "div.listing-card__text > a.listing-card__title")
                image = event.find_element(By.CSS_SELECTOR, "div.listing-card__image > picture > img.image-item")

                _event_url = _event.get_attribute("href")
                image_url = image.get_attribute("src")

                events_data["events"].append({
                    "url": _event_url,
                    "image_url": image_url
                })
            except NoSuchElementException:
                continue

        # Try to go to the next page
        try:
            time.sleep(1.5)
            # Find the current active page
            current = chromedriver.find_element(By.CSS_SELECTOR, ".pagination-button--current")
            current_page = int(current.text.strip())

            # Find all pagination links
            pages = chromedriver.find_elements(By.CSS_SELECTOR, ".pagination-button")

            # Find the next page link (if available)
            next_page = None
            for page in pages:
                try:
                    if int(page.text.strip()) == current_page + 1:
                        next_page = page
                        break
                except ValueError:
                    pass

            if not next_page:
                print("No more pages.")
                break

            # Click next page and wait to load
            chromedriver.execute_script("arguments[0].click();", next_page)
            time.sleep(1)
        except NoSuchElementException:
            break  # No more pages

    return events_data
