import aiohttp
from aiohttp import BasicAuth

async def delete_event_async(
    remote_event_id: int,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> bool:
    """
    Asynchronously deletes an event post from a WordPress site using the REST API.

    Args:
        remote_event_id (int): ID of the event post to delete.
        wp_username (str): WordPress username for authentication.
        wp_password (str): WordPress password or application password for authentication.
        wp_url (str, optional): Base URL of the WordPress REST API. Defaults to staging site.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    url = f"{wp_url}/wp/v2/events/{remote_event_id}?force=true"
    auth = BasicAuth(wp_username, wp_password)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.delete(url) as response:
                if response.status == 200 or response.status == 204:
                    return True
                else:
                    error_text = await response.text()
                    print(f"Error deleting event ID {remote_event_id}: {response.status} - {error_text}")
                    return False
        except aiohttp.ClientError as e:
            print(f"Error deleting event ID {remote_event_id}: {e}")
            return False
