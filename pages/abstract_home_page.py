from core.base_page import BasePage

class AbstractHomePage(BasePage):
    def __init__(self, page, locators: dict):
        super().__init__(page)
        self.locators = locators

    def navigate(self):
        self.go_to(self.locators['url'])

    def search(self, query: str):
        self.smart_fill(self.locators['search_input'], query)
        self.smart_click(self.locators['search_btn'])
        self.wait_for_page_load()

    def go_to_login(self):
        if "login_url" in self.locators:
            self.go_to(self.locators["login_url"])
        else:
            self.smart_click(self.locators["login_link"])
        self.wait_for_page_load()
