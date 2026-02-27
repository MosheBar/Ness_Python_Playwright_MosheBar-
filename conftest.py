import os
import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext
from typing import Generator
from config.settings import logger, GRID_URL

IS_CI = os.getenv("CI", "false").lower() == "true"

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    if GRID_URL:
        logger.info(f"Connecting to remote Playwright grid at {GRID_URL}")
        browser_instance = playwright.chromium.connect(ws_endpoint=GRID_URL)
    else:
        logger.info(f"Launching local Playwright Chromium instance (headless={IS_CI})")
        browser_instance = playwright.chromium.launch(
            headless=IS_CI,
            args=['--start-maximized']
        )
    yield browser_instance
    browser_instance.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    browser_context = browser.new_context(no_viewport=True)
    yield browser_context
    browser_context.close()
