import aiohttp
import traceback
import logging
from aiohttp import BasicAuth

async def update_event_categories_async(
    event_id: int,
    category_ids: list[int],
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> bool:
    """
    Update categories assigned to a WordPress event.

    Args:
        event_id (int): ID of the event to update.
        category_ids (list[int]): List of category IDs to assign.
        wp_username (str): WordPress username.
        wp_password (str): WordPress app password.
        wp_url (str): Base WordPress REST API URL.

    Returns:
        bool: True if update successful, False otherwise.
    """
    if not event_id:
        print("Error: event_id is required.")
        return False

    payload = {
        "event-categories": category_ids
    }

    headers = {'Content-Type': 'application/json'}

    url = f"{wp_url}/wp/v2/events/{event_id}"
    auth = BasicAuth(wp_username, wp_password)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.put(url, json=payload, headers=headers) as response:
                if response.status in (200, 201):
                    return True
                else:
                    text = await response.text()
                    print(f"Failed to update categories: {response.status} - {text}")
        except aiohttp.ClientError as e:
            print(f"AIOHTTP client error: {e}")

    return False


async def push_event_acf_to_wordpress(
    remote_event_id: int,
    remote_media_id: int,
    index_intro: str,
    intro: str,
    content: str,
    website: str,
    dates: str,
    location: str,
    cost: str,
    date_order: str,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> bool:
    """
    Update ACF fields of a WordPress event post via REST API.

    Args:
        remote_event_id (int): WordPress event post ID.
        remote_media_id (int): Media ID for the event's image.
        index_intro (str): Short introductory content.
        intro (str): Main introduction text.
        content (str): Full event content.
        website (str): Source website name.
        dates (str): Event dates string.
        location (str): Event location.
        cost (str): Event cost description.
        date_order (str): Structured date ordering string.
        wp_username (str): WordPress username.
        wp_password (str): WordPress application password.
        wp_url (str): Base URL of the WordPress site (default is staging).

    Returns:
        bool: True if update succeeds, False otherwise.
    """
    if not remote_event_id:
        logging.error("Missing event_id for ACF update.")
        return False

    payload = {
        "fields": {
            "image": remote_media_id,
            "index_intro": index_intro,
            "intro": intro,
            "content": content,
            "website": website,
            "dates": dates,
            "location": location,
            "cost": cost,
            "date_order": date_order
        }
    }

    headers = {'Content-Type': 'application/json'}

    endpoint = f"{wp_url}/acf/v3/events/{remote_event_id}"
    auth = BasicAuth(wp_username, wp_password)

    try:
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.put(endpoint, json=payload, headers=headers) as response:
                if response.status in (200, 201):
                    return True
                else:
                    error_text = await response.text()
                    logging.error(f"ACF update failed [{response.status}]: {error_text}")
    except aiohttp.ClientError as e:
        logging.error(f"AIOHTTP error: {e}\n{traceback.format_exc()}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}\n{traceback.format_exc()}")

    return False


async def update_event_title_status_async(
    event_id: int,
    title: str,
    status: str,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> bool:
    if not event_id or not title or not status:
        print("Error: event_id, title, and status are required.")
        return False

    url = f"{wp_url}/wp/v2/events/{event_id}"
    payload = {
        "title": title,
        "status": status
    }

    auth = BasicAuth(wp_username, wp_password)
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status in (200, 201):
                    return True
                else:
                    text = await response.text()
                    print(f"Failed to update title/status: {response.status} - {text}")
        except aiohttp.ClientError as e:
            print(f"HTTP error: {e}")

    return False
