import json
from selenium.webdriver import Chrome

def load_cookies_to_driver(driver: Chrome, cookies_file_path: str, target_url: str):
    """
    Load cookies into a WebDriver (Firefox or Chrome) session and go to the target URL.

    Parameters:
        driver (webdriver.Firefox or webdriver.Chrome): Selenium WebDriver instance.
        cookies_file_path (str): Path to cookies JSON file.
        target_url (str): URL to visit after setting cookies.
    """
    driver.get(target_url)

    with open(cookies_file_path, "r") as f:
        cookies = json.load(f)

    for c in cookies:
        cookie = {
            "name": c.get("name"),
            "value": c.get("value"),
        }
        # Optional fields if available
        if "domain" in c:
            cookie["domain"] = c["domain"]
        if "path" in c:
            cookie["path"] = c["path"]
        if "expiry" in c:
            cookie["expiry"] = int(c["expiry"])
        if "secure" in c:
            cookie["secure"] = c["secure"]
        if "httpOnly" in c:
            cookie["httpOnly"] = c["httpOnly"]

        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Failed to add cookie: {cookie} - {e}")

    driver.refresh()
    driver.get(target_url)
