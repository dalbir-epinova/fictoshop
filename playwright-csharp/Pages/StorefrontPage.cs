using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class StorefrontPage
{
    private readonly IPage _page;
    private readonly ILocator _productCards;

    public StorefrontPage(IPage page)
    {
        _page = page;
        _productCards = page.Locator(".product-card");
    }

    public async Task OpenAsync()
    {
        await _page.GotoAsync("/", new PageGotoOptions
        {
            WaitUntil = WaitUntilState.DOMContentLoaded,
        });
        await Expect(_page.Locator("#product-grid"))
            .ToHaveAttributeAsync("aria-busy", "false");
    }

    public async Task AssertCatalogIsVisibleAsync()
    {
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Welcome to FictoShop", Exact = true }))
            .ToBeVisibleAsync();
        await Expect(_page.Locator("#catalog")).ToBeVisibleAsync();
        Assert.That(await _productCards.CountAsync(), Is.GreaterThan(0));
    }

    public async Task<string> SearchForFirstProductAsync()
    {
        var name = await _productCards.First.Locator("h3").InnerTextAsync();
        await _page.Locator("#product-search").FillAsync(name);
        return name;
    }

    public async Task AssertOnlyProductIsVisibleAsync(string productName)
    {
        await Expect(_productCards).ToHaveCountAsync(1);
        await Expect(_productCards.First.Locator("h3")).ToHaveTextAsync(productName);
        await Expect(_page.Locator("#product-status")).ToContainTextAsync("Showing 1 of");
    }

    public async Task<string> OpenFirstProductAsync()
    {
        var name = await _productCards.First.Locator("h3").InnerTextAsync();
        await _productCards.First.Locator(".product-card-title").ClickAsync();
        return name;
    }

    public async Task AssertProductDetailsAsync(string productName)
    {
        await Expect(_page).ToHaveURLAsync(new System.Text.RegularExpressions.Regex(@"/products/\d+/view$"));
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = productName, Exact = true }))
            .ToBeVisibleAsync();
        await Expect(_page.Locator(".product-detail-price")).ToBeVisibleAsync();
        await Expect(_page.Locator(".product-detail-rating")).ToBeVisibleAsync();
        await Expect(_page.Locator("#reviews")).ToBeVisibleAsync();
    }

    public async Task<string> AddFirstAvailableProductAsync()
    {
        var card = _page.Locator(".product-card:has(button:has-text('Add to cart'):not([disabled]))").First;
        var name = await card.Locator("h3").InnerTextAsync();
        await card.GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true }).ClickAsync();
        return name;
    }

    public async Task AssertCartContainsAsync(string productName)
    {
        await Expect(_page.Locator("#cart")).ToBeVisibleAsync();
        await Expect(_page.Locator("#cart-items")).ToContainTextAsync(productName);
        await Expect(_page.Locator("#cart-total-items")).ToHaveTextAsync("1");
    }
}
