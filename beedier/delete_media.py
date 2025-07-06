import aiohttp

async def delete_media_async(
    media_id: int,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> bool:
    url = f"{wp_url}/wp/v2/media/{media_id}?force=true"
    auth = aiohttp.BasicAuth(wp_username, wp_password)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.delete(url) as response:
                if response.status in (200, 204):
                    return True
                else:
                    error_text = await response.text()
                    print(f"Failed to delete media ID {media_id}: {response.status} - {error_text}")
        except aiohttp.ClientError as e:
            print(f"Client error deleting media ID {media_id}: {e}")

    return False
