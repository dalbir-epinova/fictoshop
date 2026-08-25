# Playwright Behave test suite

End-to-end coverage for the storefront using Playwright (Python) and Behave with a Page Object Model structure.

## Setup

- Create/activate a virtual env.
- Install dependencies: `python -m pip install -r playwright_tests/requirements.txt`
- Install the browser runtime once: `python -m playwright install chromium`
- Ensure the Django app is running locally (default `http://127.0.0.1:8000`). Override with `FICTOSHOP_BASE_URL`.

## Run

- Headless (default): `behave playwright_tests/features`
- Headed: `FICTOSHOP_HEADED=1 behave playwright_tests/features` or `behave -D headed=true playwright_tests/features`
- Target a single scenario: `behave playwright_tests/features/catalog.feature --name "Guest adds a product to the cart from the catalog"`

## Structure

- `features/`: Gherkin feature files plus Behave hooks in `environment.py`.
- `features/steps/`: Step definitions bound to the features.
- `pages/`: Page Objects (shared navigation/helpers live in `BasePage`).
- `behave.ini`: Behave is configured to look at `playwright_tests/features`.
