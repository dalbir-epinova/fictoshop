using System.Text.Json;
using System.Text.RegularExpressions;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class MobilePage
{
    private readonly IPage _page;
    private readonly ScenarioState _state;

    public MobilePage(IPage page, ScenarioState state)
    {
        _page = page;
        _state = state;
    }

    public Task SetViewportAsync(int width, int height) => _page.SetViewportSizeAsync(width, height);

    public async Task AssertStorefrontFitsAsync()
    {
        var heading = _page.GetByRole(AriaRole.Heading, new() { Name = "Welcome to FictoShop" });
        var catalog = _page.Locator("#catalog");
        await Expect(heading).ToBeVisibleAsync();
        await Expect(catalog).ToBeVisibleAsync();
        await AssertInsideDocumentAsync(heading);
        await AssertInsideDocumentAsync(catalog);
    }

    public async Task AssertPrimaryControlsAsync()
    {
        Assert.That(await _page.EvaluateAsync<bool>("document.documentElement.scrollWidth <= window.innerWidth"), Is.True);
        foreach (var control in new[]
        {
            _page.GetByRole(AriaRole.Link, new() { Name = "Shop the catalog" }),
            _page.GetByLabel("Search catalog"),
            _page.GetByLabel("Sort by"),
        })
        {
            await Expect(control).ToBeVisibleAsync();
            await Expect(control).ToBeEnabledAsync();
            await AssertInsideDocumentAsync(control);
        }
    }

    public async Task AssertCartWidthAsync()
    {
        var cart = _page.Locator("#cart");
        await Expect(cart).ToBeVisibleAsync();
        await AssertInsideDocumentAsync(cart);
    }

    public async Task AssertCartLinesScrollableAsync()
    {
        var items = _page.Locator("#cart-items");
        var overflow = await items.EvaluateAsync<string>("element => getComputedStyle(element).overflowY");
        var maxHeight = await items.EvaluateAsync<string>("element => getComputedStyle(element).maxHeight");
        Assert.That(overflow, Is.AnyOf("auto", "scroll"));
        Assert.That(maxHeight, Is.Not.EqualTo("none"));
    }

    public async Task AssertCartActionsAsync()
    {
        foreach (var name in new[] { "Clear", "Checkout" })
        {
            var button = _page.GetByRole(AriaRole.Button, new() { Name = name, Exact = true });
            await Expect(button).ToBeVisibleAsync();
            await Expect(button).ToBeEnabledAsync();
            await AssertInsideDocumentAsync(button);
        }
    }

    public async Task AssertCheckoutSingleColumnAsync()
    {
        var columns = await _page.Locator(".shipping-form").EvaluateAsync<string>("element => getComputedStyle(element).gridTemplateColumns");
        Assert.That(columns.Split(' ', StringSplitOptions.RemoveEmptyEntries), Has.Length.EqualTo(1));
    }

    public async Task AssertCheckoutActionsAsync()
    {
        foreach (var control in new[]
        {
            _page.GetByRole(AriaRole.Link, new() { Name = "Back to cart", Exact = true }),
            _page.GetByRole(AriaRole.Button, new() { Name = "Place order", Exact = true }),
        })
        {
            await Expect(control).ToBeVisibleAsync();
            await AssertInsideDocumentAsync(control);
        }
    }

    public async Task LoadAndroidBundleAsync()
    {
        var index = Path.Combine(ProjectPaths.Root, "android-app", "app", "src", "main", "assets", "index.html");
        Assert.That(File.Exists(index), Is.True);
        await _page.RouteAsync("http://10.0.2.2:8000/**", HandleBundleRouteAsync);
        await _page.GotoAsync(new Uri(index).AbsoluteUri);
        await Expect(_page.Locator("#product-grid")).ToHaveAttributeAsync("aria-busy", "false");
    }

    public void AssertAndroidBase() => Assert.That(_state.RequestedUrls.Any(url => url.StartsWith("http://10.0.2.2:8000/products")), Is.True);

    public async Task LoadIosBundleAsync()
    {
        var plist = await File.ReadAllTextAsync(Path.Combine(ProjectPaths.Root, "ios-app", "fictoshop", "Info.plist"));
        var swift = await File.ReadAllTextAsync(Path.Combine(ProjectPaths.Root, "ios-app", "fictoshop", "fictoshop", "WebView.swift"));
        var project = await File.ReadAllTextAsync(Path.Combine(ProjectPaths.Root, "ios-app", "fictoshop", "fictoshop.xcodeproj", "project.pbxproj"));
        Assert.That(plist, Does.Contain("<key>API_BASE_URL</key>"));
        Assert.That(swift, Does.Contain("object(forInfoDictionaryKey: \"API_BASE_URL\")"));
        var match = Regex.Match(project, "API_BASE_URL = \"([^\"]+)\";");
        Assert.That(match.Success, Is.True);
        _state.ConfiguredIosBase = match.Groups[1].Value.TrimEnd('/');
        await _page.AddInitScriptAsync($"window.__FICTO_API_BASE__ = {JsonSerializer.Serialize(_state.ConfiguredIosBase)};");
        await _page.RouteAsync(_state.ConfiguredIosBase + "/**", HandleBundleRouteAsync);
        var index = Path.Combine(ProjectPaths.Root, "mobile-web", "index.html");
        await _page.GotoAsync(new Uri(index).AbsoluteUri);
        await Expect(_page.Locator("#product-grid")).ToHaveAttributeAsync("aria-busy", "false");
    }

    public void AssertIosBase() => Assert.That(_state.RequestedUrls.Any(url => url.StartsWith(_state.ConfiguredIosBase + "/products")), Is.True);
    public Task AssertBundleProductAsync() => Expect(_page.Locator(".product-card").Filter(new() { HasText = "Bundled mobile product" })).ToBeVisibleAsync();

    private async Task HandleBundleRouteAsync(IRoute route)
    {
        _state.RequestedUrls.Add(route.Request.Url);
        if (route.Request.Url.EndsWith("/products"))
        {
            await route.FulfillAsync(new RouteFulfillOptions
            {
                Status = 200,
                ContentType = "application/json",
                Body = "[{\"id\":9001,\"name\":\"Bundled mobile product\",\"description\":\"Product returned to a mobile bundle test.\",\"price\":19.95,\"in_stock\":5,\"image_url\":\"\",\"average_rating\":null,\"review_count\":0}]",
            });
        }
        else if (route.Request.Url.EndsWith("/cart"))
        {
            await route.FulfillAsync(new RouteFulfillOptions { Status = 200, ContentType = "application/json", Body = "{\"items\":[],\"total_items\":0,\"grand_total\":0}" });
        }
        else
        {
            await route.ContinueAsync();
        }
    }

    private async Task AssertInsideDocumentAsync(ILocator locator)
    {
        var box = await locator.BoundingBoxAsync();
        var viewport = _page.ViewportSize;
        Assert.That(box, Is.Not.Null);
        Assert.That(viewport, Is.Not.Null);
        Assert.That(box!.X, Is.GreaterThanOrEqualTo(-20));
        Assert.That(box.X + box.Width, Is.LessThanOrEqualTo(viewport!.Width));
    }
}
