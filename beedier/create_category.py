import requests
from requests.auth import HTTPBasicAuth
from typing import Optional

def create_wp_category(
    name: str,
    wp_username: str,
    wp_password: str,
    wp_url: str = "https://staging.beedier.com/wp-json"
) -> Optional[int]:
    url = f"{wp_url}/wp/v2/event-categories"
    auth = HTTPBasicAuth(wp_username, wp_password)

    payload = {"name": name}

    try:
        response = requests.post(url, json=payload, auth=auth)
        if response.status_code in (200, 201):
            data = response.json()
            return data.get("id")
        elif response.status_code == 400:
            text = response.text
            if "term_exists" in text:
                get_resp = requests.get(f"{url}?search={name}", auth=auth)
                if get_resp.status_code == 200:
                    result = get_resp.json()
                    for cat in result:
                        if cat["name"].lower() == name.lower():
                            return cat["id"]
        else:
            print(f"Failed to create category: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Requests error: {e}")

    return None
