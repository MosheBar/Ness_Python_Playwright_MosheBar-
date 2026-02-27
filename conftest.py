import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext
from typing import Generator
from config.settings import logger, GRID_URL

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """
    Override the default Playwright browser fixture to support Remote Grid 
    (Selenium Grid / Moon) via WebSocket.
    """
    if GRID_URL:
        logger.info(f"Connecting to remote Playwright grid at {GRID_URL}")
        browser_instance = playwright.chromium.connect(ws_endpoint=GRID_URL)
    else:
        logger.info("Launching local Playwright Chromium instance")
        browser_instance = playwright.chromium.launch(
            headless=False, # default for local debug, tests can override via CLI 
            args=['--start-maximized']
        )
        
    yield browser_instance
    browser_instance.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Creates an isolated context. We use no_viewport=True so the page 
    automatically adapts to the maximized browser window, showing all filters.
    """
    context = browser.new_context(no_viewport=True)
    yield context
    context.close()
