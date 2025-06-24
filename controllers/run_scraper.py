from selenium_webdriver import get_selenium_chrome_driver
from dbcore import create_event, get_config
from .get_scrapers import get_scraper_function
from .get_all_targets import get_all_targets

env_config = get_config()

def run_scraper(category: str, target: str):
    if target == "all":
        # Collect all targets under this category
        targets = [t for (c, t) in get_all_targets() if c == category]
    else:
        targets = [target]

    chromedriver = get_selenium_chrome_driver(
        headless=False,
        chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
    )

    for tgt in targets:
        print(f"Scraping: {category} {tgt}")
        scraper_func = get_scraper_function(category, tgt)
        data = scraper_func(chromedriver=chromedriver)
        for event in data.get("events", []):
            create_event(
                event_url=event.get("url"),
                website_name=data.get("website_name"),
                image_url=event.get("image_url")
            )
