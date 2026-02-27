import json
import os
import pytest
import allure
from pages.abstract_home_page import AbstractHomePage
from pages.abstract_login_page import AbstractLoginPage
from pages.abstract_search_results_page import AbstractSearchResultsPage
from pages.abstract_item_page import AbstractItemPage
from pages.abstract_cart_page import AbstractCartPage
from config.settings import logger

# Due to config load, we just import these constants:
try:
    from config.settings import USER_EMAIL, USER_PASSWORD
except ImportError:
    USER_EMAIL = os.getenv("USER_EMAIL")
    USER_PASSWORD = os.getenv("USER_PASSWORD")

def get_test_cases():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_data.json")
    with open(data_path, 'r') as f:
        data = json.load(f)
    cases = []
    for site, queries in data.items():
        for q in queries:
            cases.append((site, q["query"], q["maxPrice"], q["limit"]))
    return cases

def load_locators(site: str):
    locator_path = os.path.join(os.path.dirname(__file__), "..", "data", "locators", f"{site}_locators.json")
    with open(locator_path, 'r') as f:
        return json.load(f)

@allure.feature("E-Commerce Checkout Flow")
@pytest.mark.parametrize("site, query, maxPrice, limit", get_test_cases())
def test_ecommerce_end_to_end(page, site, query, maxPrice, limit):
    allure.dynamic.title(f"Test checkout flow for {site} with query '{query}'")
    
    # 1. Load locators dynamically based on site
    locators = load_locators(site)

    # 2. Init Pages
    home_page = AbstractHomePage(page, locators.get("home", {}))
    login_page = AbstractLoginPage(page, locators.get("login", {}))
    search_page = AbstractSearchResultsPage(page, locators.get("search", {}))
    item_page = AbstractItemPage(page, locators.get("item", {}))
    cart_page = AbstractCartPage(page, locators.get("cart", {}))

    # 3. Execution
    home_page.navigate()

    # Authentication - Optional Guest mode
    if USER_EMAIL and USER_PASSWORD:
        home_page.go_to_login()
        login_page.login(USER_EMAIL, USER_PASSWORD)
    else:
        logger.info("No credentials provided. Proceeding as Guest checkout.")

    home_page.search(query)

    # Retrieve items based on constraints
    item_urls = search_page.searchItemsByNameUnderPrice(query, maxPrice, limit)
    
    if not item_urls:
        logger.warning(f"No items found for criteria. Skipping add-to-cart.")
    else:
        # Loop to add all urls to Cart
        item_page.addItemsToCart(item_urls)

    # Assert Final Constraints + Tracing
    cart_page.assertCartTotalNotExceeds(maxPrice, len(item_urls))
