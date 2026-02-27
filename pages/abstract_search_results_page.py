from core.base_page import BasePage
from config.settings import logger
import allure

class AbstractSearchResultsPage(BasePage):
    def __init__(self, page, locators: dict):
        super().__init__(page)
        self.locators = locators

    def searchItemsByNameUnderPrice(self, query: str, maxPrice: float, limit: int = 5) -> list[str]:
        self.wait_for_page_load()
        if "price_filter_input_max" in self.locators and "price_filter_submit" in self.locators:
            self._apply_price_filter(maxPrice)
        else:
            logger.warning("Price filter locators not configured — skipping price filter")
        return self._collect_item_urls(limit)

    def _apply_price_filter(self, maxPrice: float) -> None:
        with allure.step(f"Apply max price filter ({int(maxPrice)})"):
            price_input = self._find_price_input()
            if price_input is None:
                logger.error("Price filter input NOT found — skipping price filter")
                return
            try:
                price_input.scroll_into_view_if_needed()
                price_was_set = self._fill_price_with_retry(price_input, str(int(maxPrice)))
                logger.info(f"Price fill result: {price_was_set}")
                if price_was_set:
                    self._submit_price_filter()
            except Exception as e:
                logger.error(f"Price filter interaction failed: {e}")
                allure.attach(str(e), name="Price Filter Error")

    def _find_price_input(self):
        for selector in self.locators["price_filter_input_max"]:
            try:
                price_input_element = self.page.locator(selector).first
                price_input_element.wait_for(state="visible", timeout=5000)
                logger.info(f"Price filter input found: {selector}")
                return price_input_element
            except Exception:
                logger.warning(f"Price filter selector not visible: {selector}")
        return None

    def _fill_price_with_retry(self, price_input, expected_value: str, max_retries: int = 3) -> bool:
        for attempt in range(1, max_retries + 1):
            price_input.click()
            price_input.fill(expected_value)
            price_input.press("Tab")
            actual_value = price_input.input_value()
            if actual_value == expected_value:
                logger.info(f"Max price set to {expected_value} (attempt {attempt})")
                return True
            logger.warning(
                f"Price input mismatch on attempt {attempt}: "
                f"expected '{expected_value}', got '{actual_value}' — retrying"
            )
        logger.error(f"Failed to set price to '{expected_value}' after {max_retries} attempts")
        return False

    def _submit_price_filter(self) -> None:
        self.wait_for_page_load()
        for submit_selector in self.locators["price_filter_submit"]:
            try:
                submit_btn = self.page.locator(submit_selector).first
                submit_btn.wait_for(state="visible", timeout=3000)
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=8000):
                    submit_btn.click()
                logger.info(f"Price filter submitted via: {submit_selector}")
                return
            except Exception:
                continue
        logger.warning("Price filter submit button not found — filter may not have applied")

    def _collect_item_urls(self, limit: int) -> list[str]:
        collected_urls = []
        self.wait_for_page_load()
        with allure.step(f"Extracting up to {limit} item URLs"):
            while len(collected_urls) < limit:
                self.page.wait_for_selector(
                    self.locators["item_links"][0], state="attached", timeout=10000
                )
                for item_link in self.page.locator(self.locators["item_links"][0]).all():
                    if len(collected_urls) >= limit:
                        break
                    href = item_link.get_attribute("href")
                    if href and href not in collected_urls:
                        collected_urls.append(href)

                if len(collected_urls) >= limit:
                    break

                try:
                    with self.page.expect_navigation(wait_until="domcontentloaded", timeout=5000):
                        self.smart_click(self.locators["next_page_btn"], timeout_ms=3000)
                except Exception:
                    break

        return collected_urls[:limit]
