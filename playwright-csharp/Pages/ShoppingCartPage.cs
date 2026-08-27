using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class ShoppingCartPage
{
    private readonly IPage _page;
    private readonly ILocator _cart;

    public ShoppingCartPage(IPage page)
    {
        _page = page;
        _cart = page.Locator("#cart");
    }

    public int? LastCartResponseStatus { get; private set; }
    public ILocator CartItems => _page.Locator("#cart-items .cart-item");
    public ILocator ProductCard(string name) => _page.Locator(".product-card").Filter(new() { HasText = name });
    public ILocator CartLine(string name) => CartItems.Filter(new() { HasText = name });

    public async Task OpenAsync()
    {
        await _page.GotoAsync(TestSettings.BaseUrl);
        await Expect(_page.Locator("#product-grid")).ToHaveAttributeAsync("aria-busy", "false");
    }

    public async Task AddProductAsync(string name, int quantity = 1)
    {
        var card = ProductCard(name);
        if (await card.CountAsync() == 0)
        {
            await OpenAsync();
            card = ProductCard(name);
        }
        await Expect(card).ToHaveCountAsync(1);
        var input = card.Locator(".quantity-input");
        await input.FillAsync(quantity.ToString());
        await input.DispatchEventAsync("change");
        await card.GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true }).ClickAsync();
        await Expect(_page.Locator("#app-toast")).ToContainTextAsync($"Added {quantity}");
        await Expect(_page.Locator("#app-toast")).ToContainTextAsync(name);
        await Expect(CartLine(name)).ToBeVisibleAsync();
    }

    public async Task SelectQuantityAsync(string name, int quantity)
    {
        var input = ProductCard(name).Locator(".quantity-input");
        await input.FillAsync(quantity.ToString());
        await input.DispatchEventAsync("change");
        await Expect(input).ToHaveValueAsync(quantity.ToString());
    }

    public async Task AddSelectedProductAsync(string name)
    {
        var card = ProductCard(name);
        var quantity = int.Parse(await card.Locator(".quantity-input").InputValueAsync());
        await card.GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true }).ClickAsync();
        await Expect(_page.Locator("#app-toast")).ToContainTextAsync($"Added {quantity}");
        await Expect(CartLine(name)).ToBeVisibleAsync();
    }

    public Task AssertHiddenAsync() => Expect(_cart).ToBeHiddenAsync();
    public Task AssertVisibleAsync() => Expect(_cart).ToBeVisibleAsync();
    public Task AssertProductInCartAsync(string name) => Expect(CartLine(name)).ToBeVisibleAsync();
    public Task AssertProductNotInCartAsync(string name) => Expect(CartLine(name)).ToHaveCountAsync(0);
    public Task AssertTotalItemsAsync(int quantity) => Expect(_page.Locator("#cart-total-items")).ToHaveTextAsync(quantity.ToString());
    public Task AssertGrandTotalAsync(decimal total) => Expect(_page.Locator("#cart-grand-total")).ToHaveTextAsync($"${total:F2}");
    public Task AssertLineQuantityAsync(string name, int quantity) => Expect(CartLine(name).Locator(".muted")).ToContainTextAsync($"{quantity} ");
    public Task AssertOneLineAsync(string name) => Expect(CartLine(name)).ToHaveCountAsync(1);
    public Task ScrollAsync() => _page.EvaluateAsync("window.scrollTo(0, document.body.scrollHeight)");

    public async Task AssertInsideViewportAsync()
    {
        var box = await _cart.BoundingBoxAsync();
        var viewport = _page.ViewportSize;
        Assert.That(box, Is.Not.Null);
        Assert.That(viewport, Is.Not.Null);
        Assert.Multiple(() =>
        {
            Assert.That(box!.X, Is.GreaterThanOrEqualTo(0));
            Assert.That(box.Y, Is.GreaterThanOrEqualTo(0));
            Assert.That(box.X + box.Width, Is.LessThanOrEqualTo(viewport!.Width));
            Assert.That(box.Y + box.Height, Is.LessThanOrEqualTo(viewport.Height));
        });
    }

    public async Task RemoveProductAsync(string name)
    {
        var line = CartLine(name);
        await line.GetByRole(AriaRole.Button, new() { Name = "Remove", Exact = true }).ClickAsync();
        await Expect(line).ToHaveCountAsync(0);
    }

    public async Task ClearAsync()
    {
        await _page.GetByRole(AriaRole.Button, new() { Name = "Clear", Exact = true }).ClickAsync();
        await AssertHiddenAsync();
    }

    public async Task ReloadAsync()
    {
        await _page.ReloadAsync();
        await Expect(_page.Locator("#product-grid")).ToHaveAttributeAsync("aria-busy", "false");
    }

    public async Task AttemptOverStockAsync(string name, int stock)
    {
        var card = ProductCard(name);
        var attempted = stock + 1;
        await card.Locator(".quantity-input").EvaluateAsync("(element, value) => { element.max = value; element.value = value; }", attempted.ToString());
        var responseTask = _page.WaitForResponseAsync(response =>
            response.Url.TrimEnd('/').EndsWith("/cart", StringComparison.Ordinal) && response.Request.Method == "POST");
        await card.GetByRole(AriaRole.Button, new() { Name = "Add to cart", Exact = true }).ClickAsync();
        LastCartResponseStatus = (await responseTask).Status;
    }

    public void AssertRequestRejected() => Assert.That(LastCartResponseStatus, Is.EqualTo(400));
    public Task AssertStockErrorAsync(int stock, string name) => Expect(_page.Locator("#cart-message")).ToHaveTextAsync($"Only {stock} units left of {name}");
    public Task AssertCatalogStockAsync(string name, int stock) => Expect(ProductCard(name).Locator(".badge")).ToHaveTextAsync($"{stock} in stock");
}
