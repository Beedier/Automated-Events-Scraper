import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

def get_selenium_chrome_driver(
    headless: bool = True,
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    download_dir: str = None,
    binary_path=None,
    chromedriver_path="/usr/local/bin/chromedriver"
):
    options = Options()
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")

    if user_agent:
        options.add_argument(f"user-agent={user_agent}")

    if binary_path:
        options.binary_location = binary_path

    if download_dir:
        prefs = {
            "download.default_directory": os.path.abspath(download_dir),
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(executable_path=chromedriver_path),
        options=options
    )

    return driver
