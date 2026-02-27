# E-Commerce Playwright Automation Framework

A robust, abstract, Data-Driven E2E testing framework built with **Python**, **Playwright**, and **Pytest**.  
Designed to run resiliently across diverse e-commerce sites (e.g. eBay) using a clean POM architecture with smart locator fallback.

---

## Architecture

### 1. Abstract Page Object Model (POM)
All page logic lives in abstract page classes (`abstract_home_page.py`, `abstract_search_results_page.py`, `abstract_item_page.py`, `abstract_cart_page.py`, `abstract_login_page.py`).  
**No locators are hardcoded** in Python — they are injected at runtime from site-specific JSON files.

### 2. Smart Locators & Resilience
`BasePage` (`core/base_page.py`) implements fallback-driven interaction methods:
- `smart_click(locators[])` — tries each locator in order; logs which succeeded/failed
- `smart_fill(locators[])` — same for inputs
- `smart_get_text(locators[])` — same for reading text

Each element defines **alternative locators** in the JSON. If the primary fails (A/B test, DOM change), the next is tried automatically. Failed attempts are logged with the locator name and attempt number. A screenshot is captured on final failure.

### 3. Data-Driven Configuration
- **Test inputs**: `data/test_data.json` — site, query, maxPrice, limit
- **Locators**: `data/locators/{site}_locators.json` — fully external, per-site
- Adding a new site requires only a new locators JSON — no Python changes

### 4. Remote Grid / Moon Support
The `conftest.py` browser fixture checks `GRID_URL` in `.env`.  
When set, it connects via WebSocket (`playwright.chromium.connect(ws_endpoint=...)`), enabling execution on Selenium Grid / Moon with full session isolation per test.

---

## 4 Core Functions

| Function | Location | Description |
|---|---|---|
| `login(email, password)` | `AbstractLoginPage` | Fills credentials and submits. Skipped gracefully when no creds provided (Guest mode). |
| `searchItemsByNameUnderPrice(query, maxPrice, limit)` | `AbstractSearchResultsPage` | Applies price filter, collects up to `limit` item URLs, paginates if needed. |
| `addItemsToCart(urls)` | `AbstractItemPage` | Navigates each URL, selects random variants (listbox/select/button), clicks Add to Cart, takes screenshot. |
| `assertCartTotalNotExceeds(budgetPerItem, itemsCount)` | `AbstractCartPage` | Reads cart subtotal, asserts total ≤ budgetPerItem × itemsCount. Saves screenshot + trace. |

---

## Prerequisites

```bash
python -m venv venv

# Windows (PowerShell)
.\\venv\\Scripts\\Activate.ps1

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install --with-deps chromium
```

---

## Environment Setup

Edit `.env` before running:

```dotenv
# Optional: Remote Grid WebSocket endpoint (Moon / Selenium Grid)
# e.g. ws://moon.example.local:4444/playwright
GRID_URL=

# Optional: Login credentials — leave empty to run as Guest
USER_EMAIL=
USER_PASSWORD=
```

---

## CI/CD — GitHub Actions

The workflow in `.github/workflows/playwright.yml` runs automatically on:
- **Every push** to `main` / `master`
- **Every pull request** to `main` / `master`
- **Nightly** at 00:00 UTC (scheduled cron)

After each run it generates and publishes an Allure report to **GitHub Pages** (the `gh-pages` branch), making results accessible via a public URL without any manual steps.

Credentials and `GRID_URL` are stored as **GitHub Secrets** (Settings → Secrets → Actions) and injected at runtime — never stored in the repo.

---

## Running Tests

```bash
# Run all tests — allure results are generated automatically via pytest.ini
pytest tests

# Open the Allure report
allure serve allure-results
```

> `pytest.ini` configures `--alluredir=allure-results` and `-v` automatically via `addopts`, so no extra flags needed.

---

## Constraints & Assumptions

| Topic | Decision |
|---|---|
| **Authentication** | Login is **optional**. If `USER_EMAIL` / `USER_PASSWORD` are empty in `.env`, the test runs as a Guest (no login step). This is intentional to support environments without valid credentials and to handle eBay's anti-bot flows. |
| **Currency** | Currency symbol validation is **not enforced**. The framework extracts the first numeric value from the cart subtotal text and compares it against the budget threshold. This avoids locale/currency failures (eBay may display currency differently by region). |
| **Variants** | Variants (size, colour, etc.) are selected **randomly** from available options. Items with no variants are handled gracefully and proceed directly to Add to Cart. |
| **Pagination** | If fewer than `limit` items are found on the first results page, the framework automatically paginates until `limit` is reached or no more pages exist. |
| **Parallelism** | Parallel browser execution is supported via Selenium Grid / Moon through `GRID_URL` in `.env`. Locally, tests run sequentially unless `pytest-xdist` is added. |

---

## Project Structure

```
├── config/
│   └── settings.py              # Loads .env, logger, constants
├── core/
│   └── base_page.py             # Smart locator methods, screenshots, go_to
├── pages/
│   ├── abstract_home_page.py
│   ├── abstract_login_page.py
│   ├── abstract_search_results_page.py
│   ├── abstract_item_page.py
│   └── abstract_cart_page.py
├── data/
│   ├── test_data.json           # Data-driven test inputs
│   └── locators/
│       └── ebay_locators.json   # Per-site locator definitions
├── tests/
│   └── test_ecommerce.py        # Parametrized E2E test
├── conftest.py                  # Browser / context fixtures, Grid support
├── pytest.ini                   # Allure, markers configuration
└── .env                         # Credentials & Grid URL (not committed)
```