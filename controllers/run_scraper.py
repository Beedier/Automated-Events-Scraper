from selenium_webdriver import get_selenium_chrome_driver
from dbcore import create_event, get_config
from .get_scrapers import get_scraper_function
from .get_all_targets import get_all_targets
from dbcore import fetch_events_without_web_content, fetch_events_by_website
from dbcore import set_event_web_content

env_config = get_config()


def run_scraper(category: str, target: str, include_existing: bool = False):
    """
    Run scraper based on category and target.

    Args:
        category (str): Scraper category ('event-url' or 'event-web-content').
        target (str): Specific target to scrape or 'all' for all targets.
        include_existing (bool): If True, include events that already have web content
                                 (only affects 'event-web-content' category).
    """
    # Resolve list of targets to process
    if target == "all":
        targets = [t for (c, t) in get_all_targets() if c == category]
    else:
        targets = [target]

    # Initialize Selenium Chrome driver once for all targets
    chromedriver = get_selenium_chrome_driver(
        headless=False,
        chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
    )

    if category == 'event-url':
        for tgt in targets:
            print(f"Scraping: {category} {tgt}")
            scraper_func = get_scraper_function(category, tgt)
            data = scraper_func(chromedriver=chromedriver)

            # Create events in DB from scraped data
            for event in data.get("events", []):
                create_event(
                    event_url=event.get("url"),
                    website_name=data.get("website_name"),
                    image_url=event.get("image_url")
                )

    elif category == 'event-web-content':
        for tgt in targets:
            print(f"Scraping: {category} {tgt}")
            scraper_func = get_scraper_function(category, tgt)

            # Fetch events either with or without web content depending on flag
            if include_existing:
                events = fetch_events_by_website(website_name=tgt)
            else:
                events = fetch_events_without_web_content(website_name=tgt)

            # Scrape and update web content for each event
            for event in events:
                content = scraper_func(
                    event_url=event.event_url,
                    chromedriver=chromedriver
                )

                has_updated = set_event_web_content(
                    event_id=event.id,
                    web_content=content,
                    generated_content=False
                )

                if has_updated and content:
                    print(f"Event ID: {event.id}, Web content updated and set generated content false.")
                else:
                    print(f"Event ID: {event.id}, set web content null and set generated content false.")
    else:
        # Category not recognized, no operation
        pass
