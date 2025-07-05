import os
import aiohttp
import asyncio
from typing import Optional

async def upload_media_async(
    file_path: str,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> Optional[int]:
    """
    Asynchronously uploads a media file to a WordPress site via REST API.

    Returns:
        Optional[int]: Media item ID if upload is successful, else None.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return None

    file_name = os.path.basename(file_path)
    url = f"{wp_url}/wp/v2/media"
    headers = {
        "Content-Disposition": f"attachment; filename={file_name}"
    }

    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()

        auth = aiohttp.BasicAuth(wp_username, wp_password)

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.post(
                url,
                headers=headers,
                data=file_content
            ) as response:
                if response.status in (200, 201):
                    json_response = await response.json()
                    return int(json_response.get("id"))
                else:
                    text = await response.text()
                    print(f"Upload failed: {response.status} - {text}")
    except aiohttp.ClientError as e:
        print(f"Client error during media upload: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None
