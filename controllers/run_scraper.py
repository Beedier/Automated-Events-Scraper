import asyncio
from selenium_webdriver import get_selenium_chrome_driver
from .get_scrapers import get_scraper_function
from .get_all_targets import get_all_targets
from dbcore import (
    Image, create_event, get_config,
    fetch_events_without_web_content,
    fetch_events_by_website,
    fetch_events_with_web_content,
    fetch_events_with_non_generated_content,
    fetch_images_without_image_path,
    set_event_generated_content,
    fetch_images_without_remote_media_id,
    set_remote_media_id,
    set_event_web_content,
    set_processed_image_path,
    fetch_events_without_remote_event_id,
    fetch_events_with_remote_event_id_and_categories,
    set_remote_event_id, Event,
    fetch_ready_events_for_publishing, PublishStatusEnum,
    set_event_publish_status,
    set_event_remote_event_id,
    set_event_remote_media_id,
    fetch_events_delete_from_wordpress,
    fetch_images_delete_from_wordpress,
    fetch_events_with_content_and_generated_flag,
)

from beedier import (
    upload_media_async,
    create_event_async,
    update_event_categories_async,
    push_event_acf_to_wordpress,
    delete_event_async,
    delete_media_async
)

from library import ImageProcessor, parse_json_to_dict, get_existing_event_urls, CalendarMinuteRateLimiter
from gemini_ai import create_prompt, generate_text_with_gemini
from ollama_ai import export_fine_tuning_events_to_json

env_config = get_config()

gemini_rate_limiter = CalendarMinuteRateLimiter(requests_per_minute=5)


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

        # get existing dataset
        existing_urls = get_existing_event_urls()

        for tgt in targets:
            print(f"Scraping: {category} {tgt}")
            scraper_func = get_scraper_function(category, tgt)
            data = scraper_func(chromedriver=chromedriver)

            # Create events in DB from scraped data
            for event in data.get("events", []):
                if event.get("url") in existing_urls:
                    print(f"✅ Skipping existing event: {event.get('url')}")
                    continue

                _event = create_event(
                    event_url=event.get("url"),
                    website_name=data.get("website_name"),
                    image_url=event.get("image_url")
                )
                if _event:
                    print(f"Event Created, Event ID: {_event.id}")

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

            # Fetch images without images depending on flag
            images = fetch_images_without_image_path(website_name=tgt)

            for image in images:
                image_processor = ImageProcessor(
                    image_url=image.image_url
                )

                processed_image_path = image_processor.process(
                    overlay_path=target_config[tgt].get('overlay_path'),
                    save_dir=target_config[tgt].get('save_dir')
                )

                has_updated = set_processed_image_path(
                    image_id=image.id,
                    image_path=processed_image_path
                )

                if has_updated:
                    print(
                        f"Updated image path. Image ID: {image.id}"
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

                gemini_rate_limiter.wait_if_needed()

                raw_response = generate_text_with_gemini(
                    api_key=env_config.get("GEMINI_API_KEY"),
                    prompt=prompt
                )

                parsed_data = parse_json_to_dict(json_data=raw_response)

                if parsed_data:
                    has_updated = set_event_generated_content(
                        event_id=event.id,
                        category_names=parsed_data.get("Categories"),
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

    elif category == 'upload-media':

        for tgt in targets:
            print(f"Upload media to remote website: {category} {tgt}")

            # Fetch images without remote media id
            images = fetch_images_without_remote_media_id(website_name=tgt)

            async def upload_and_update(_image: Image):
                media_id = await upload_media_async(
                    file_path=_image.image_path,
                    wp_username=env_config.get('WP_USERNAME'),
                    wp_password=env_config.get('WP_PASSWORD'),
                    wp_url=env_config.get('WP_URL')
                )
                if media_id:
                    set_remote_media_id(
                        image_id=_image.id,
                        remote_media_id=media_id
                    )

                    print(f"Updated Remote media ID. Image ID: {_image.id}")

            async def run_all():
                await asyncio.gather(*(upload_and_update(img) for img in images))

            # Run the async uploads from sync code
            asyncio.run(run_all())

    elif category == 'create-event':

        for tgt in targets:
            print(f"Create event to remote website: {category} {tgt}")

            # Fetch events without remote event id
            events = fetch_events_without_remote_event_id(website_name=tgt)

            async def create_and_update(_event: Event):
                remote_event_id = await create_event_async(
                    wp_username=env_config.get('WP_USERNAME'),
                    wp_password=env_config.get('WP_PASSWORD'),
                    wp_url=env_config.get('WP_URL'),
                    title=_event.title
                )
                if remote_event_id:
                    set_remote_event_id(
                        event_id=_event.id,
                        remote_event_id=remote_event_id
                    )

                    print(f"New Remote Event Created. Event ID: {_event.id}. Title: {_event.title}")

            async def run_all():
                await asyncio.gather(*(create_and_update(evnt) for evnt in events))

            # Run the async uploads from sync code
            asyncio.run(run_all())

    elif category == 'update-event-category':

        for tgt in targets:

            print(f"Update Event Category to remote website: {category} {tgt}")

            # Fetch events that already have remote_event_id and category mappings

            events = fetch_events_with_remote_event_id_and_categories(website_name=tgt)


            async def update_category(_event: Event):

                category_ids = [

                    cat.remote_category_id

                    for cat in _event.categories

                    if cat.remote_category_id is not None

                ]

                if not category_ids:
                    print(f"Skipping Event ID {_event.id} — No valid remote_category_id found.")

                    return

                success = await update_event_categories_async(

                    event_id=_event.remote_event_id,

                    category_ids=category_ids,

                    wp_username=env_config.get('WP_USERNAME'),

                    wp_password=env_config.get('WP_PASSWORD'),

                    wp_url=env_config.get('WP_URL')

                )

                if success:

                    print(f"✅ Updated categories for Event ID: {_event.id}")

                else:

                    print(f"❌ Failed to update categories for Event ID: {_event.id}")


            async def run_all():

                await asyncio.gather(*(update_category(evnt) for evnt in events))


            asyncio.run(run_all())

    elif category == 'update-event':

        for tgt in targets:

            print(f"Update Event content to remote website: {category} {tgt}")

            # Fetch events that ready for publishing
            events = fetch_ready_events_for_publishing(website_name=tgt)

            async def update_and_set_status_draft(_event: Event):
                success = await push_event_acf_to_wordpress(
                    remote_event_id=_event.remote_event_id,
                    remote_media_id=_event.image.remote_media_id,

                    index_intro=_event.index_intro,
                    intro=_event.intro,
                    content=_event.content,
                    website=_event.event_url,
                    dates=_event.dates,

                    location=_event.location,
                    cost=_event.cost,

                    date_order=_event.date_order,
                    wp_username=env_config.get('WP_USERNAME'),
                    wp_password=env_config.get('WP_PASSWORD'),
                    wp_url=env_config.get('WP_URL')
                )

                if success:
                    # Mark event as draft
                    set_event_publish_status(
                        event_id=_event.id,
                        status=PublishStatusEnum.DRAFT
                    )

                    print(f"Updated Event Content. Status: Draft, Event ID: {_event.id}")

            async def run_all():

                await asyncio.gather(*(update_and_set_status_draft(evnt) for evnt in events))

            asyncio.run(run_all())


    elif category == 'delete-event':

        for tgt in targets:

            print(f"Delete Event from remote website: {category} {tgt}")

            # Fetch events that ready to delete
            events = fetch_events_delete_from_wordpress(website_name=tgt)

            async def delete_and_set_remote_event_id_and_set_status(_event: Event):
                success = await delete_event_async(
                    remote_event_id=_event.remote_event_id,
                    wp_username=env_config.get('WP_USERNAME'),
                    wp_password=env_config.get('WP_PASSWORD'),
                    wp_url=env_config.get('WP_URL')
                )

                if success:
                    # Mark event as unsynced
                    set_event_publish_status(
                        event_id=_event.id,
                        status=PublishStatusEnum.UNSYNCED
                    )

                    set_event_remote_event_id(
                        event_id=_event.id,
                        remote_event_id=None
                    )

                    print(f"Deleted Event. Status: Unsynced, Event ID: {_event.id}")

            async def run_all():

                await asyncio.gather(*(delete_and_set_remote_event_id_and_set_status(evnt) for evnt in events))

            asyncio.run(run_all())

    elif category == 'delete-media':

        for tgt in targets:

            print(f"Delete Media from remote website: {category} {tgt}")

            # Fetch media that ready to delete
            images = fetch_images_delete_from_wordpress(website_name=tgt)

            async def delete_and_set_remote_media_id(_image: Image):
                success = await delete_media_async(
                    media_id=_image.remote_media_id,
                    wp_username=env_config.get('WP_USERNAME'),
                    wp_password=env_config.get('WP_PASSWORD'),
                    wp_url=env_config.get('WP_URL')
                )

                if success:

                    set_event_remote_media_id(
                        image_id=_image.id,
                        remote_media_id=None
                    )

                    print(f"Deleted Media, Image ID: {_image.id}")

            async def run_all():

                await asyncio.gather(*(delete_and_set_remote_media_id(img) for img in images))

            asyncio.run(run_all())

    elif category == 'generate-fine-tuning-dataset':

        all_data = []

        for tgt in targets:
            print(f"Fetching events with generated content for website: {tgt}")

            events = fetch_events_with_content_and_generated_flag(website_name=tgt)

            print(f"Found {len(events)} events for {tgt}")

            all_data.extend(events)

        print(f"Total events collected for fine-tuning: {len(all_data)}")

        print("Exporting fine-tuning dataset to JSON...")

        export_fine_tuning_events_to_json(

            events=all_data,

            file_path=env_config.get('FINE_TUNING_DATASET')

        )

        print("Fine-tuning dataset export completed.")

    else:
        # Category not recognized, no operation
        pass
