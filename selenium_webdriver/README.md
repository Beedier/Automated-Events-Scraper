# selenium_webdriver

A lightweight utility to configure and launch a Selenium Chrome WebDriver with custom options like headless mode, custom user-agent, download directory, and binary paths. Ideal for automated scraping and testing environments, including CI/CD pipelines like GitHub Actions.

## Features
- Headless Chrome support
- Custom Chrome binary and chromedriver path
- Set custom user-agent
- Set custom download directory
- Safe defaults for CI environments

## Installation
No package manager setup required. Just include `selenium_webdriver.py` in your project.

Dependencies:
```bash
pip install selenium
```

## Function: `get_selenium_chrome_driver()`

### Parameters:
- `headless` (bool): Run Chrome in headless mode (default: `True`)
- `user_agent` (str): Optional user-agent string
- `download_dir` (str): Optional download directory path
- `binary_path` (str): Path to the Chrome binary (default: `/usr/bin/google-chrome`)
- `chromedriver_path` (str): Path to the ChromeDriver executable (required)

### Returns:
- `selenium.webdriver.Chrome` instance

## Example Usage
```python
from selenium_webdriver import get_selenium_chrome_driver

driver = get_selenium_chrome_driver(
    headless=True,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    binary_path="/usr/bin/google-chrome",
    chromedriver_path="/usr/local/bin/chromedriver"
)

driver.get("https://example.com")
print(driver.page_source)
driver.quit()
```

## License
MIT

