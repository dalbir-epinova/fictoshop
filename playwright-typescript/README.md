# Fictoshop Playwright TypeScript

This project is the TypeScript counterpart to `playwright-python` and `playwright-csharp`. It uses:

- TypeScript with strict type checking
- Microsoft Playwright for browser automation
- Cucumber.js for Gherkin/BDD
- Node.js as the test runtime
- Page Objects to keep selectors out of step definitions

The suite mirrors all seven feature files from `playwright-python` and contains 78 scenarios covering storefront, cart, checkout, authentication and reviews, Django administration, APIs, and responsive mobile behavior.

## Prerequisites

Install Node.js on macOS:

```bash
brew install node
node --version
npm --version
```

The Django application must already have its Python virtual environment at `.venv`. The TypeScript suite uses that environment to create isolated fixtures and clean them up after every scenario.

## First-time setup

From the repository root:

```bash
cd playwright-typescript
npm install
npm run install:browsers
```

## Run tests

Start Django from the repository root in one terminal:

```bash
source .venv/bin/activate
python manage.py runserver
```

Run the TypeScript tests in another terminal:

```bash
cd playwright-typescript
npm test
```

The browser is visible by default. Run headless with:

```bash
npm run test:headless
```

Run one feature area by tag:

```bash
npm run build
npx cucumber-js --tags "@storefront"
npx cucumber-js --tags "@cart"
npx cucumber-js --tags "@checkout"
npx cucumber-js --tags "@authentication"
npx cucumber-js --tags "@admin"
npx cucumber-js --tags "@api"
npx cucumber-js --tags "@responsive"
```

Run smoke scenarios:

```bash
npm run test:smoke
```

Target another Fictoshop environment:

```bash
FICTOSHOP_BASE_URL=https://example.test npm test
```

Failed scenarios save a full-page screenshot in `artifacts/`. Every run also produces an HTML report at `reports/cucumber-report.html`.

## Settings

Default browser mode and the 10-second Playwright timeout are configured in `src/support/settings.ts`:

```typescript
export const settings = {
  baseUrl: (process.env.FICTOSHOP_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, ""),
  headed: process.env.HEADED?.toLowerCase() !== "false",
  timeout: 10_000
};
```

## Structure

```text
features/      Gherkin scenarios
src/pages/     Page Objects and selectors
src/steps/     Cucumber step definitions
src/support/   Browser hooks, API client, Django fixtures, state, and settings
```

The suite runs sequentially because the demo application's cart is stored globally in server memory. Each scenario snapshots the database, clears the cart, and removes only the data it created.
