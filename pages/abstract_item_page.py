from core.base_page import BasePage
import allure
import random

class AbstractItemPage(BasePage):
    def __init__(self, page, locators: dict):
        super().__init__(page)
        self.locators = locators

    def addItemsToCart(self, urls: list[str]):
        for item_index, url in enumerate(urls):
            with allure.step(f"Adding item {item_index+1} to cart - URL: {url}"):
                self.go_to(url)
                self.wait_for_page_load()
                self.page.wait_for_timeout(2000)
                self._select_variants_if_exist()
                self.page.wait_for_timeout(1500)
                self.smart_click(self.locators["add_to_cart_btn"])
                self.page.wait_for_timeout(2000)
                self.take_screenshot(f"item_added_{item_index+1}")

    def _select_variants_if_exist(self):
        from config.settings import logger

        if "variant_dropdowns" in self.locators and self.locators["variant_dropdowns"]:
            dropdown_selectors = self.locators["variant_dropdowns"]
            available_option_selector = self.locators["variant_options"][0] if "variant_options" in self.locators else None

            try:
                listbox_buttons = self.page.locator(dropdown_selectors[0]).all()
                if listbox_buttons:
                    logger.info(f"Found {len(listbox_buttons)} custom listbox variant(s) via '{dropdown_selectors[0]}'")
                    for listbox_btn in listbox_buttons:
                        try:
                            listbox_btn.click()
                            self.page.wait_for_timeout(400)
                            if not available_option_selector:
                                continue
                            listbox_id = listbox_btn.get_attribute("aria-controls")
                            if listbox_id:
                                scoped_option_selector = f"#{listbox_id} {available_option_selector}"
                                available_options = self.page.locator(scoped_option_selector).all()
                            else:
                                available_options = [opt for opt in self.page.locator(available_option_selector).all() if opt.is_visible()]
                            if available_options:
                                chosen_option = random.choice(available_options)
                                chosen_option.scroll_into_view_if_needed()
                                chosen_option.click()
                            self.page.wait_for_timeout(600)
                        except Exception as e:
                            logger.warning(f"Custom listbox variant selection failed: {e}")
                    return
            except Exception:
                pass

            for native_select_selector in dropdown_selectors[1:]:
                try:
                    native_selects = self.page.locator(native_select_selector).all()
                    if native_selects:
                        logger.info(f"Found {len(native_selects)} native select variant(s) via '{native_select_selector}'")
                        for native_select in native_selects:
                            all_options = native_select.locator("option").all()
                            selectable_values = [
                                opt.get_attribute("value") for opt in all_options
                                if opt.get_attribute("value") and opt.get_attribute("value") != "-1"
                            ]
                            if selectable_values:
                                native_select.select_option(value=random.choice(selectable_values))
                                self.page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue

        if "variant_buttons" in self.locators:
            for button_selector in self.locators["variant_buttons"]:
                try:
                    variant_buttons = self.page.locator(button_selector).all()
                    if variant_buttons:
                        random.choice(variant_buttons).click()
                        self.page.wait_for_timeout(800)
                        return
                except Exception:
                    continue

        from config.settings import logger as _logger
        _logger.info("No variants found — proceeding without selection")
