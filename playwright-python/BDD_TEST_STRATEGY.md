# BDD/TDD test strategy

The `.feature` files in this directory are the executable-specification backlog for Playwright. They describe expected behavior but are not wired to Behave; the project continues to use Python, pytest, and pytest-playwright.

## TDD workflow

For each scenario:

1. Select one scenario and create one clearly named `test_...` function.
2. Arrange only the data required by that scenario, preferably through an API helper or Django test-data command.
3. Run the new test and confirm that it fails for the expected reason (red).
4. Implement the smallest product change needed to satisfy it (green).
5. Refactor test helpers and application code while all tests stay green.

Do not implement every scenario in one large test. Each scenario should be independently runnable and should explain one behavior when it fails.

## Recommended test layers

- Use Playwright browser tests for navigation, rendering, forms, JavaScript behavior, responsive layout, and complete user journeys.
- Use Playwright's API request context for API scenarios that support browser setup or represent an external consumer.
- Keep calculation, model, serializer, validation, and transaction edge cases in `shop/tests.py`; duplicating every backend assertion in the browser suite adds cost without much confidence.
- Use a small number of `@smoke` scenarios as the fastest deployment check. Run the complete `@regression` set less frequently.

## Isolation rules for this application

- Clear the cart through `DELETE /cart` before and after every cart or checkout test.
- Do not depend on product database IDs or the order of preloaded products.
- Create uniquely named test users and products when a scenario mutates data.
- Clean up records created through the admin or API.
- Run cart and checkout scenarios serially until the global in-memory cart is replaced by a session-scoped cart. Parallel workers currently share cart state.
- Create a new browser context when testing session isolation.
- Avoid fixed sleeps; wait for visible UI state or a specific network response.

## Suggested Python layout

```text
playwright-python/
  features/                    BDD requirements in Gherkin
  pages/                       Optional page objects when repetition appears
  tests/
    test_storefront.py
    test_cart.py
    test_checkout.py
    test_authentication.py
    test_reviews.py
    test_api.py
    test_admin.py
    test_responsive.py
  conftest.py                  Browser settings, base URL, and fixtures
```

Page objects and shared helpers should be introduced only after two or more tests need the same interaction. This keeps the first tests readable and prevents premature abstraction.
