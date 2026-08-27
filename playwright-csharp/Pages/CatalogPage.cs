using System.Globalization;
using System.Text.RegularExpressions;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class CatalogPage
{
    private readonly IPage _page;

    public CatalogPage(IPage page)
    {
        _page = page;
    }

    public ILocator ProductCards => _page.Locator(".product-card");

    public ILocator ProductCard(string name) => ProductCards.Filter(new LocatorFilterOptions
    {
        Has = _page.GetByRole(AriaRole.Heading, new() { Name = name, Exact = true }),
    });

    public async Task OpenAsync()
    {
        await _page.GotoAsync(TestSettings.BaseUrl);
        await WaitForCatalogAsync();
    }

    public async Task AssertOpenAsync() => await Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/");

    public async Task AssertHeadingAndCatalogAsync()
    {
        await WaitForCatalogAsync();
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Welcome to FictoShop", Exact = true })).ToBeVisibleAsync();
        await Expect(_page.Locator("#catalog")).ToBeVisibleAsync();
        Assert.That(await ProductCards.CountAsync(), Is.GreaterThan(0));
    }

    public async Task AssertCardsHavePurchasingInformationAsync()
    {
        await WaitForCatalogAsync();
        var count = await ProductCards.CountAsync();
        Assert.That(count, Is.GreaterThan(0));
        for (var index = 0; index < count; index++)
        {
            var card = ProductCards.Nth(index);
            await Expect(card.Locator("h3")).Not.ToHaveTextAsync("");
            await Expect(card.Locator(".product-price")).ToContainTextAsync("$");
            await Expect(card.Locator(".badge")).ToBeVisibleAsync();
        }
    }

    public Task AssertAvailableAddEnabledAsync(string name) =>
        Expect(ProductCard(name).GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true })).ToBeEnabledAsync();

    public Task OpenProductAsync(string name) => ProductCard(name).Locator(".product-card-title").ClickAsync();

    public async Task AssertProductDetailAsync(ProductRecord product)
    {
        await Expect(_page).ToHaveURLAsync(new Regex($@"/products/{product.Id}/view$"));
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = product.Name, Exact = true })).ToBeVisibleAsync();
        await Expect(_page.GetByText(product.Description, new() { Exact = true })).ToBeVisibleAsync();
        await Expect(_page.Locator(".product-detail-price")).ToContainTextAsync($"${product.Price:F2}");
        await Expect(_page.Locator(".product-detail-rating")).ToBeVisibleAsync();
        await Expect(_page.Locator("#reviews")).ToBeVisibleAsync();
    }

    public Task SearchAsync(string query) => _page.Locator("#product-search").FillAsync(query);

    public async Task AssertOnlyProductAsync(string name)
    {
        await Expect(ProductCards).ToHaveCountAsync(1);
        await Expect(ProductCards.First.Locator("h3")).ToHaveTextAsync(name);
    }

    public Task AssertCatalogStatusAsync(int matches, int total) =>
        Expect(_page.Locator("#product-status")).ToContainTextAsync($"Showing {matches} of {total}");

    public async Task AssertNoProductsAsync()
    {
        await Expect(ProductCards).ToHaveCountAsync(0);
        await Expect(_page.Locator("#product-empty")).ToBeVisibleAsync();
    }

    public Task ClearSearchAsync() => SearchAsync("");
    public Task AssertProductCountAsync(int count) => Expect(ProductCards).ToHaveCountAsync(count);
    public Task SelectSortAsync(string label) => _page.Locator("#product-sort").SelectOptionAsync(new SelectOptionValue { Label = label });

    public async Task<IReadOnlyList<decimal>> DisplayedPricesAsync()
    {
        var values = await ProductCards.Locator(".product-price").AllTextContentsAsync();
        return values.Select(value => decimal.Parse(value.Replace("$", "").Replace(",", ""), CultureInfo.InvariantCulture)).ToList();
    }

    public async Task<IReadOnlyList<int>> DisplayedStocksAsync()
    {
        var result = new List<int>();
        for (var index = 0; index < await ProductCards.CountAsync(); index++)
        {
            var value = await ProductCards.Nth(index).Locator(".quantity-input").GetAttributeAsync("max");
            result.Add(int.Parse(value ?? "0", CultureInfo.InvariantCulture));
        }

        return result;
    }

    public Task EnableInStockOnlyAsync() => _page.Locator("#product-in-stock").CheckAsync();
    public Task AssertProductHiddenAsync(string name) => Expect(ProductCard(name)).ToHaveCountAsync(0);

    public async Task AssertOutOfStockControlsAsync(string name)
    {
        var card = ProductCard(name);
        await Expect(card.Locator(".badge")).ToHaveTextAsync("Out of stock");
        await Expect(card.Locator(".quantity-input")).ToBeDisabledAsync();
        await Expect(card.Locator(".quantity-btn").First).ToBeDisabledAsync();
        await Expect(card.Locator(".quantity-btn").Last).ToBeDisabledAsync();
        await Expect(card.GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true })).ToBeDisabledAsync();
    }

    public Task DecreaseInitialQuantityAsync(string name) => ProductCard(name).Locator(".quantity-btn").First.ClickAsync();
    public Task AssertQuantityAsync(string name, int quantity) => Expect(ProductCard(name).Locator(".quantity-input")).ToHaveValueAsync(quantity.ToString());

    public async Task IncreaseBeyondStockAsync(string name, int stock)
    {
        var plus = ProductCard(name).Locator(".quantity-btn").Last;
        for (var index = 0; index < stock + 2; index++)
        {
            await plus.ClickAsync();
        }
    }

    public Task ExploreApiAsync() => _page.GetByRole(AriaRole.Link, new() { Name = "Explore the API", Exact = true }).ClickAsync();
    public Task AssertProductsEndpointAsync() => Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/products");

    public async Task AssertApiCatalogProductsAsync()
    {
        var body = await _page.Locator("body").InnerTextAsync();
        Assert.That(body, Does.Contain("name"));
    }

    public Task AssertSignedInUserAsync(string username) => Expect(_page.Locator(".nav-user")).ToHaveTextAsync($"Signed in as {username}");
    public Task AssertLogoutButtonAsync() => Expect(_page.Locator("header").GetByRole(AriaRole.Button, new() { Name = "Log out", Exact = true })).ToBeVisibleAsync();
    public Task AssertProductVisibleAsync(string name) => Expect(ProductCard(name)).ToBeVisibleAsync();
    public Task AssertProductStockAsync(string name, int stock) => Expect(ProductCard(name).Locator(".badge")).ToHaveTextAsync($"{stock} in stock");

    public async Task AssertProductImageAsync(string name)
    {
        var image = ProductCard(name).GetByRole(AriaRole.Img, new() { Name = $"{name} photo" });
        await image.ScrollIntoViewIfNeededAsync();
        await Expect(image).ToBeVisibleAsync();
        await Expect(image).ToHaveAttributeAsync("src", new Regex("/images/uploads/"));
        await Expect(image).ToHaveJSPropertyAsync("complete", true, new() { Timeout = 15_000 });
        Assert.That(await image.EvaluateAsync<bool>("element => element.naturalWidth > 0"), Is.True);
    }

    private Task WaitForCatalogAsync() => Expect(_page.Locator("#product-grid")).ToHaveAttributeAsync("aria-busy", "false");
}
