import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def get_event_urls_from_bco_org(
    chromedriver: WebDriver,
    base_page_url: str = "https://www.bco.org.uk/events",
    max_months: int = 12
) -> dict:
    """
    Scrapes event URLs and image URLs from the British Council for Offices (BCO) events page.

    This function opens the event listing page, switches to list view,
    paginates through up to `max_months` of events, and collects the event detail URLs and image URLs.

    Args:
        chromedriver (WebDriver): Selenium WebDriver instance.
        base_page_url (str): URL of the BCO events listing page.
        max_months (int): Number of calendar months to scrape (pages).

    Returns:
        dict: Dictionary containing the website name and list of events,
              where each event has a 'url' and 'image_url'.
    """
    events_data = {
        "website_name": "bco-org",
        "events": []
    }

    # Open the events page
    chromedriver.get(url=base_page_url)

    list_view_btn = None
    next_month_btn = None

    # Try to make both "list view" and "next month" buttons visible and clickable
    while True:
        try:
            list_view_btn = WebDriverWait(chromedriver, 5).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "button[title='list view']"))
            )
            next_month_btn = WebDriverWait(chromedriver, 5).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "button[title='Next month']"))
            )

            # Ensure both buttons are in viewport
            chromedriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", list_view_btn)
            chromedriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'end'});", next_month_btn)

            # Ensure both are interactable
            WebDriverWait(chromedriver, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[title='list view']")))
            WebDriverWait(chromedriver, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Next month']")))
            break

        except TimeoutException:
            chromedriver.execute_script("window.scrollBy(0, 25);")
            time.sleep(0.5)

    # Switch to list view using JS to avoid interception
    chromedriver.execute_script("arguments[0].click();", list_view_btn)
    time.sleep(1)

    # Iterate through each month's page
    for index in range(max_months):
        try:
            # Wait for event items to be visible
            event_links = WebDriverWait(chromedriver, 2).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "a.calendar-list-item"))
            )

            for event in event_links:
                try:
                    url = event.get_attribute("href")
                    image_tag = event.find_element(By.CLASS_NAME, "event-image")
                    image_url = image_tag.get_attribute("src")

                    if url and image_url:
                        events_data["events"].append({
                            "url": url,
                            "image_url": image_url
                        })
                except NoSuchElementException:
                    continue  # Skip if image not found

            time.sleep(2)
        except TimeoutException:
            print(f"⚠️  No events found on page {index + 1}")

        # Go to next month's page
        try:
            chromedriver.execute_script("arguments[0].click();", next_month_btn)
        except (ElementClickInterceptedException, TimeoutException) as e:
            print(f"⚠️  Failed to click 'Next month' button: {type(e).__name__}")
            break

    return events_data
