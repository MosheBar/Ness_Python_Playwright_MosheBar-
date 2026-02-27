from core.base_page import BasePage
import allure
import re

class AbstractCartPage(BasePage):
    def __init__(self, page, locators: dict):
        super().__init__(page)
        self.locators = locators

    def assertCartTotalNotExceeds(self, budgetPerItem: float, itemsCount: int) -> None:
        if "url" in self.locators and not self.page.url.startswith(self.locators["url"]):
            self.go_to(self.locators["url"])

        self.wait_for_network_idle()

        try:
            cart_subtotal_text = self.smart_get_text(self.locators["cart_subtotal_text"])
            numeric_match = re.search(r'[\d,\.]+', cart_subtotal_text)
            assert numeric_match, f"Could not extract numeric value from text: {cart_subtotal_text}"

            cart_total = float(numeric_match.group().replace(',', ''))
            budget_threshold = budgetPerItem * itemsCount

            with allure.step(f"Asserting {cart_total} <= {budget_threshold}"):
                assert cart_total <= budget_threshold, f"Cart total {cart_total} exceeds budget limit {budget_threshold}"

            allure.attach(f"Success: Cart total {cart_total} is within limit {budget_threshold}", name="Cart Assertion Pass")

        except Exception as e:
            allure.attach(str(e), name="Cart Assertion Failed")
            raise e
        finally:
            self.take_screenshot("Cart_Page_Final")
            try:
                trace_path = "cart_trace.zip"
                self.page.context.tracing.stop(path=trace_path)
                allure.attach.file(trace_path, name="Playwright Cart Trace", attachment_type="application/zip")
            except Exception:
                pass
