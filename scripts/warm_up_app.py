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
# Waking up or redeploying the app can take a few minutes. Per page, both together
# below the job's timeout (20 min), so that the failure screenshot gets saved
APP_START_TIMEOUT_S = 240
# Loading the Dailies took ~2 s locally; Community Cloud has far fewer CPU cores
LOADING_TIMEOUT_S = 120
FAILURE_SCREENSHOT = "warm_up_failure.png"


def _find_app_frame(page: Page, timeout_s: float) -> Frame:
    """The frame with the Streamlit app: Community Cloud embeds it in an iframe."""
    start = time.monotonic()
    next_report = start + 30
    while time.monotonic() < start + timeout_s:
        wake_up = page.get_by_text(WAKE_UP_BUTTON)
        if wake_up.count() > 0:
            print("The app is asleep, waking it up")
            wake_up.first.click()
        for frame in page.frames:
            if frame.locator('[data-testid="stApp"]').count() > 0:
                return frame
        if time.monotonic() > next_report:
            print(f"Still waiting for the app; frames: {[f.url for f in page.frames]}")
            next_report += 30
        page.wait_for_timeout(2000)
    raise PlaywrightTimeoutError(f"The app didn't start within {timeout_s} s")


def _wait_until_idle(frame: Frame, timeout_s: float):
    """Wait until the script run triggered by the last click has finished."""
    frame.page.wait_for_timeout(1000)  # Until the run has started
    status = frame.locator('[data-testid="stStatusWidget"]')
    status.wait_for(state="hidden", timeout=timeout_s * 1000)


def _open_page_and_select(page: Page, url: str, option_name: str):
    """Select an option of a segmented control on the page."""
    start = time.monotonic()
    print(f"Opening {url}")
    page.goto(url)
    frame = _find_app_frame(page, APP_START_TIMEOUT_S)
    # Streamlit renders the options as <button role="radio">, so they aren't found
    # with the role "button"
    option = frame.get_by_role("radio", name=re.compile(re.escape(option_name)))
    option.first.click(timeout=LOADING_TIMEOUT_S * 1000)
    _wait_until_idle(frame, LOADING_TIMEOUT_S)
    print(f"{url}: '{option_name}' loaded after {time.monotonic() - start:.0f} s")


def warm_up(app_url: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            _open_page_and_select(page, f"{app_url}/oracle", "TGG Dailies")
            _open_page_and_select(page, f"{app_url}/quiz", "TGG Dailies")
        except PlaywrightTimeoutError:
            # The workflow attaches it to the run, to see what the browser saw
            page.screenshot(path=FAILURE_SCREENSHOT, full_page=True)
            raise
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
