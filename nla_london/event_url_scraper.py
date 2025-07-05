import time
from selenium.webdriver.ie.webdriver import WebDriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin
from library import build_url_with_params


def scroll_entire_page_slowly(driver: WebDriver, step: int = 300, delay: float = 0.5):
    height = driver.execute_script("return document.body.scrollHeight")

    # Scroll down slowly
    for pos in range(0, height, step):
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(delay)

    # Scroll up slowly
    for pos in range(height, 0, -step):
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(delay)


def click_all_load_more(driver: WebDriver, max_clicks: int = 50, wait: float = 1.5):
    prev_event_count = 0
    for _ in range(max_clicks):
        try:
            # Count current events
            events = driver.find_elements(By.CSS_SELECTOR, "div.listing-preview-photo-fit")
            current_event_count = len(events)

            button = driver.find_element(By.CSS_SELECTOR, "div.show-more > button")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            time.sleep(0.5)

            if button.is_displayed() and button.is_enabled():
                driver.execute_script("arguments[0].click();", button)
                time.sleep(wait)

                # Wait for new content to load
                for _ in range(20):  # wait up to 10s
                    events = driver.find_elements(By.CSS_SELECTOR, "div.listing-preview-photo-fit")
                    if len(events) > current_event_count:
                        break
                    time.sleep(0.5)

                # Stop if no new content added
                if len(events) == prev_event_count:
                    break
                prev_event_count = len(events)
            else:
                break
        except (NoSuchElementException, ElementClickInterceptedException):
            break


def get_event_urls_from_nla_london(
    chromedriver: WebDriver,
    base_page_url: str = "https://nla.london/"
) -> dict:
    """
    Scrapes event URLs and image URLs from nla What's On page using Selenium.

    Args:
        chromedriver (WebDriver): Selenium WebDriver instance.
        base_page_url (str, optional): Base URL of the nla events listing page.

    Returns:
        dict: A dictionary containing website name and list of events with 'url' and 'image_url'.
    """
    events_data = {
        "website_name": "nla",
        "events": []
    }

    # Build and load the first page
    page_url = build_url_with_params(
        base_url=base_page_url,
        path='events'
    )
    chromedriver.get(url=page_url)

    # Click all "Load More" buttons to load full list
    click_all_load_more(chromedriver)

    scroll_entire_page_slowly(chromedriver)  # force lazy elements to load

    # Wait for all items to load
    try:
        events = WebDriverWait(driver=chromedriver, timeout=30).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.listing-preview-photo-fit"))
        )

        for event in events:
            soup = BeautifulSoup(event.get_attribute("innerHTML"), "html.parser")

            url = soup.select_one('a[href]')
            image = soup.select_one('img[src]')

            if url and image:
                events_data["events"].append({
                    "url": urljoin(base_page_url, url.get('href')),
                    "image_url": urljoin(base_page_url, image.get('src'))
                })
    except TimeoutException:
        print("No element located :(")

    return events_data
