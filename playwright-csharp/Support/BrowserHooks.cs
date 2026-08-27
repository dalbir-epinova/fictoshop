using Microsoft.Playwright;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Support;

[Binding]
public sealed class BrowserHooks
{
    private readonly ScenarioContext _scenarioContext;
    private IPlaywright? _playwright;
    private IBrowser? _browser;
    private IBrowserContext? _browserContext;

    public BrowserHooks(ScenarioContext scenarioContext)
    {
        _scenarioContext = scenarioContext;
    }

    [BeforeScenario(Order = 0)]
    public async Task StartBrowserAsync()
    {
        _playwright = await Playwright.CreateAsync();
        _browser = await _playwright.Chromium.LaunchAsync(new BrowserTypeLaunchOptions
        {
            Headless = !TestSettings.Headed,
        });
        _browserContext = await _browser.NewContextAsync(new BrowserNewContextOptions
        {
            BaseURL = TestSettings.BaseUrl,
            ViewportSize = new ViewportSize { Width = 1440, Height = 900 },
        });

        var page = await _browserContext.NewPageAsync();
        page.SetDefaultTimeout(10_000);
        page.SetDefaultNavigationTimeout(10_000);

        _scenarioContext.Set(page);
        _scenarioContext.Set(new Pages.StorefrontPage(page));

        await ClearCartAsync();
    }

    [AfterScenario(Order = 100)]
    public async Task StopBrowserAsync()
    {
        if (_scenarioContext.TestError is not null && _scenarioContext.TryGetValue<IPage>(out var page))
        {
            var artifactDirectory = Path.Combine(AppContext.BaseDirectory, "artifacts");
            Directory.CreateDirectory(artifactDirectory);
            var safeName = string.Concat(
                _scenarioContext.ScenarioInfo.Title.Select(character =>
                    Path.GetInvalidFileNameChars().Contains(character) ? '_' : character));
            await page.ScreenshotAsync(new PageScreenshotOptions
            {
                Path = Path.Combine(artifactDirectory, $"{safeName}.png"),
                FullPage = true,
            });
        }

        await ClearCartAsync();

        if (_browserContext is not null)
        {
            await _browserContext.DisposeAsync();
        }

        if (_browser is not null)
        {
            await _browser.DisposeAsync();
        }

        _playwright?.Dispose();
    }

    private static async Task ClearCartAsync()
    {
        using var client = new HttpClient { BaseAddress = new Uri(TestSettings.BaseUrl) };
        using var response = await client.DeleteAsync("/cart");
        response.EnsureSuccessStatusCode();
    }
}
