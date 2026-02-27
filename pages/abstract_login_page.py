from core.base_page import BasePage
import allure

class AbstractLoginPage(BasePage):
    def __init__(self, page, locators: dict):
        super().__init__(page)
        self.locators = locators

    def login(self, email: str, password: str):
        if not email or not password:
            return

        with allure.step(f"Login with {email}"):
            self.smart_fill(self.locators["username_input"], email)
            self.smart_click(self.locators["continue_btn"])
            self.smart_fill(self.locators["password_input"], password)
            self.smart_click(self.locators["submit_btn"])
            self.wait_for_network_idle()
