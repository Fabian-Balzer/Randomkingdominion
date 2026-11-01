"""Open the deployed app in a headless browser, so that the TGG Dailies are loaded
into the caches of the Kingdom Oracle and the quiz before a visitor needs them.

The Tests workflow runs this after the test suite, which gives Community Cloud a few
minutes to pick up the push; Community Cloud doesn't signal when it's done. A sleeping
app (12 hours without traffic) is woken up first.

    pip install playwright
    python -m playwright install --with-deps chromium
    python scripts/warm_up_app.py [--url https://randomkingdominion.streamlit.app]
"""

import argparse
import re
import sys
import time

from playwright.sync_api import Frame, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

APP_URL = "https://randomkingdominion.streamlit.app"
# The page Community Cloud shows while an app sleeps
WAKE_UP_BUTTON = "Yes, get this app back up!"
# Waking up or redeploying the app can take a few minutes
APP_START_TIMEOUT_S = 300
# Loading the Dailies took ~2 s locally; Community Cloud has far fewer CPU cores
LOADING_TIMEOUT_S = 180


def _find_app_frame(page: Page, timeout_s: float) -> Frame:
    """The frame with the Streamlit app: Community Cloud embeds it in an iframe."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        wake_up = page.get_by_role("button", name=WAKE_UP_BUTTON)
        if wake_up.count() > 0:
            print("The app is asleep, waking it up")
            wake_up.first.click()
        for frame in page.frames:
            if frame.locator('[data-testid="stApp"]').count() > 0:
                return frame
        page.wait_for_timeout(2000)
    raise PlaywrightTimeoutError(f"The app didn't start within {timeout_s} s")


def _wait_until_idle(frame: Frame, timeout_s: float):
    """Wait until the script run triggered by the last click has finished."""
    frame.page.wait_for_timeout(1000)  # Until the run has started
    status = frame.locator('[data-testid="stStatusWidget"]')
    status.wait_for(state="hidden", timeout=timeout_s * 1000)


def _open_page_and_click(page: Page, url: str, button_name: str):
    start = time.monotonic()
    page.goto(url)
    frame = _find_app_frame(page, APP_START_TIMEOUT_S)
    button = frame.get_by_role("button", name=re.compile(re.escape(button_name)))
    button.first.click(timeout=LOADING_TIMEOUT_S * 1000)
    _wait_until_idle(frame, LOADING_TIMEOUT_S)
    print(f"{url}: '{button_name}' loaded after {time.monotonic() - start:.0f} s")


def warm_up(app_url: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            _open_page_and_click(page, f"{app_url}/oracle", "TGG Dailies")
            _open_page_and_click(page, f"{app_url}/quiz", "TGG Dailies")
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default=APP_URL, help="The deployed app.")
    args = parser.parse_args()
    try:
        warm_up(args.url.rstrip("/"))
    except PlaywrightTimeoutError as e:
        print(f"Warming up failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
