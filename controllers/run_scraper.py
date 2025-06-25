from selenium_webdriver import get_selenium_chrome_driver
from dbcore import create_event, get_config
from .get_scrapers import get_scraper_function
from .get_all_targets import get_all_targets
from dbcore import fetch_events_without_web_content, fetch_events_by_website
from dbcore import fetch_events_with_web_content, fetch_events_with_non_generated_content
from dbcore import fetch_events_without_image_path, set_event_generated_content
from dbcore import set_event_web_content, set_processed_image_path
from library import ImageProcessor, parse_json_to_dict
from gemini_ai import create_prompt, generate_text_with_gemini

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

    if category == 'event-url':
        # Initialize Selenium Chrome driver once for all targets
        chromedriver = get_selenium_chrome_driver(
            headless=False,
            chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
        )

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
        # Initialize Selenium Chrome driver once for all targets
        chromedriver = get_selenium_chrome_driver(
            headless=False,
            chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
        )

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
    elif category == 'process-image':
        # Static config for each target
        target_config = {
            "riba": {
                "overlay_path": "images/overlay/RIBA_logo.png",
                "save_dir": "images/process-image/riba"
            },
            "nla": {
                "overlay_path": "images/overlay/NLA_logo.png",
                "save_dir": "images/process-image/nla"
            },
            "bco-org": {
                "overlay_path": "images/overlay/BCO_logo.png",
                "save_dir": "images/process-image/bco-org"
            },
            "event-bright": {
                # "overlay_path": "images/overlay/EVENTBRITE_logo.png",
                "overlay_path": None,
                "save_dir": "images/process-image/event-bright"
            }
        }

        for tgt in targets:
            print(f"Processing: {category} {tgt}")

            # Fetch events without images depending on flag
            events = fetch_events_without_image_path(website_name=tgt)

            for event in events:
                image_processor = ImageProcessor(
                    image_url=event.image.image_url
                )

                processed_image_path = image_processor.process(
                    overlay_path=target_config[tgt].get('overlay_path'),
                    save_dir=target_config[tgt].get('save_dir')
                )

                has_updated = set_processed_image_path(
                    event_id=event.id,
                    image_path=processed_image_path
                )

                if has_updated:
                    print(
                        f"Updated image path. Event ID: {event.id}, Image ID: {event.image.id}."
                    )
                else:
                    print("Update Error")

    elif category == 'generate-content':

        for tgt in targets:
            print(f"Generating Content: {category} {tgt}")

            # Fetch events either with or without web content depending on flag
            if include_existing:
                events = fetch_events_with_web_content(website_name=tgt)
            else:
                events = fetch_events_with_non_generated_content(website_name=tgt)

            for event in events:
                prompt = create_prompt(input_text=event.web_content)

                raw_response = generate_text_with_gemini(
                    api_key=env_config.get("GEMINI_API_KEY"),
                    prompt=prompt
                )

                parsed_data = parse_json_to_dict(json_data=raw_response)

                if parsed_data:
                    has_updated = set_event_generated_content(
                        event_id=event.id,
                        category=parsed_data.get("Category"),
                        title=parsed_data.get("Title"),
                        index_intro=parsed_data.get("IndexIntro"),
                        intro=parsed_data.get("Intro"),
                        content=parsed_data.get("Content"),
                        dates=parsed_data.get("Dates"),
                        date_order=parsed_data.get("DateOrder"),
                        location=parsed_data.get("Location"),
                        cost=parsed_data.get("Cost")
                    )

                    if has_updated:
                        print(
                            f"ID: {event.id}, Event Updated. Title: {parsed_data.get('Title')}"
                        )

    else:
        # Category not recognized, no operation
        pass
