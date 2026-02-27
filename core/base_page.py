import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config.settings import logger
import allure

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url: str):
        with allure.step(f"Navigate to {url}"):
            self.page.goto(url)

    def _execute_with_smart_locators(self, action_name: str, locators: list[str], action_func, timeout_ms: int = 5000):
        last_exception = None
        for attempt_index, selector in enumerate(locators):
            try:
                element = self.page.locator(selector).first
                with allure.step(f"Attempting '{action_name}' with locator: {selector}"):
                    logger.info(f"Attempting '{action_name}' via locator [{attempt_index+1}/{len(locators)}]: {selector}")
                    action_func(element, timeout=timeout_ms)
                    logger.info(f"Successfully executed '{action_name}' on locator: {selector}")
                    return element
            except PlaywrightTimeoutError as e:
                logger.warning(f"Timeout executing '{action_name}' on locator: {selector}")
                last_exception = e
            except Exception as e:
                logger.warning(f"Unexpected error executing '{action_name}' on locator: {selector}. Error: {e}")
                last_exception = e

        failure_message = f"Failed to execute '{action_name}' after trying all locators: {locators}. Last Error: {last_exception}"
        logger.error(failure_message)
        failure_screenshot = self.page.screenshot()
        allure.attach(failure_screenshot, name=f"failed_{action_name}", attachment_type=allure.attachment_type.PNG)
        raise Exception(failure_message)

    def smart_click(self, locators: list[str], timeout_ms: int = 5000):
        def _click(element, timeout):
            element.click(timeout=timeout)
        self._execute_with_smart_locators("click", locators, _click, timeout_ms)

    def smart_fill(self, locators: list[str], text: str, timeout_ms: int = 5000):
        def _fill(element, timeout):
            element.fill(text, timeout=timeout)
        self._execute_with_smart_locators(f"fill ('{text}')", locators, _fill, timeout_ms)

    def smart_get_text(self, locators: list[str], timeout_ms: int = 5000) -> str:
        extracted_texts = []
        def _get_text(element, timeout):
            element.wait_for(state="visible", timeout=timeout)
            extracted_texts.append(element.inner_text())
        self._execute_with_smart_locators("get_text", locators, _get_text, timeout_ms)
        return extracted_texts[0] if extracted_texts else ""

    def take_screenshot(self, name: str):
        screenshot_bytes = self.page.screenshot()
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)

    def wait_for_page_load(self):
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_network_idle(self):
        self.page.wait_for_load_state("networkidle")
