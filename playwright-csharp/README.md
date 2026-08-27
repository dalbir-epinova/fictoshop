# Fictoshop Playwright C#

This project is the C# counterpart to `playwright-python`. It uses:

- .NET 8
- Microsoft Playwright for browser automation
- Reqnroll for Gherkin/BDD
- NUnit as the test runner
- Page Objects to keep selectors out of step definitions

## Prerequisites

Install the .NET 8 SDK on macOS:

```bash
brew install dotnet@8
echo 'export PATH="/opt/homebrew/opt/dotnet@8/bin:$PATH"' >> ~/.zprofile
echo 'export DOTNET_ROOT="/opt/homebrew/opt/dotnet@8/libexec"' >> ~/.zprofile
source ~/.zprofile
dotnet --version
```

## First-time setup

From the repository root:

```bash
cd playwright-csharp
dotnet restore
dotnet build
pwsh bin/Debug/net8.0/playwright.ps1 install chromium
```

If `pwsh` is unavailable, install PowerShell first:

```bash
brew install --cask powershell
```

## Run tests

Start Django from the repository root in one terminal:

```bash
source .venv/bin/activate
python manage.py runserver
```

Run the C# tests in another terminal:

```bash
cd playwright-csharp
dotnet test
```

The C# suite mirrors all seven feature files from `playwright-python` and currently contains 78 generated scenarios covering storefront, cart, checkout, authentication and reviews, Django admin, APIs, and responsive mobile behavior. The local Django `.venv` is also used to create isolated test fixtures and clean them up after each scenario.

Run one feature area by tag:

```bash
dotnet test --filter "TestCategory=storefront"
dotnet test --filter "TestCategory=cart"
dotnet test --filter "TestCategory=checkout"
dotnet test --filter "TestCategory=authentication"
dotnet test --filter "TestCategory=admin"
dotnet test --filter "TestCategory=api"
dotnet test --filter "TestCategory=responsive"
```

Run only smoke scenarios:

```bash
dotnet test --filter "TestCategory=smoke"
```

Run with a visible browser:

```bash
HEADED=true dotnet test
```

Target a different Fictoshop environment:

```bash
FICTOSHOP_BASE_URL=https://example.test dotnet test
```

Failed scenarios save a full-page screenshot below the test output directory in `artifacts/`.

## Structure

```text
Features/    Gherkin scenarios
Pages/       Page Objects and selectors
Steps/       Reqnroll step definitions
Support/     Browser lifecycle, API client, Django fixtures, and environment configuration
```

The suite runs sequentially because the demo application's shopping cart is stored globally in server memory. Each scenario clears the cart before and after execution.
