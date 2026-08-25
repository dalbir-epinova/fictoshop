# Playwright tests in Python

This folder contains a minimal Playwright test suite written in Python and run with pytest.

BDD requirements are documented as Gherkin scenarios under `features/`. See `BDD_TEST_STRATEGY.md` for the recommended red-green-refactor workflow and test-isolation rules. The feature files are specifications; tests are implemented with pytest rather than Behave.

## Setup

Activate the project's virtual environment, then install the test dependencies:

```bash
python -m pip install -r playwright-pyton/requirements.txt
```

Install Chromium for Playwright:

```bash
python -m playwright install chromium
```

## Run

Start the Django server in one terminal:

```bash
python manage.py runserver
```

Run the example test from a second terminal with the virtual environment activated:

```bash
python -m pytest playwright-pyton
```

To watch the browser while the test runs:

```bash
python -m pytest playwright-pyton --headed
```

The test uses `http://127.0.0.1:8000` by default. Set `FICTOSHOP_BASE_URL` to test another environment.
