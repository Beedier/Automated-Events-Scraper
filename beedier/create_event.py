import aiohttp
from aiohttp import BasicAuth
from typing import Optional


async def create_event_async(
    wp_username: str,
    wp_password: str,
    title: str,
    wp_url: str = "https://staging.beedier.com/wp-json",
    status: str = "draft"
) -> Optional[int]:
    if not title:
        print("Error: Title must be provided.")
        return None

    url = f"{wp_url}/wp/v2/events"
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
                    data = await response.json()
                    return int(data.get("id"))
                else:
                    text = await response.text()
                    print(f"Error: {response.status}, {text}")
        except aiohttp.ClientError as e:
            print(f"HTTP error: {e}")

    return None
