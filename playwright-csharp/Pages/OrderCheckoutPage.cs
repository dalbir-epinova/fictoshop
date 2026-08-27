using System.Text.RegularExpressions;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class OrderCheckoutPage
{
    private static readonly Dictionary<string, string> FieldIds = new()
    {
        ["Full name"] = "#id_full_name",
        ["Email"] = "#id_email",
        ["Phone"] = "#id_phone",
        ["Address"] = "#id_address",
        ["Postal code"] = "#id_postal_code",
        ["City"] = "#id_city",
        ["Country"] = "#id_country",
    };

    private readonly IPage _page;

    public OrderCheckoutPage(IPage page)
    {
        _page = page;
    }

    public int? OrderId { get; private set; }
    public Task OpenAsync() => _page.GotoAsync(TestSettings.BaseUrl + "/checkout");
    public Task AssertStorefrontAsync() => Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/");

    public async Task AssertShippingPageAsync()
    {
        await Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/checkout");
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Shipping details" })).ToBeVisibleAsync();
    }

    public async Task AssertShippingFieldsAsync()
    {
        foreach (var label in FieldIds.Keys)
        {
            await Expect(_page.GetByLabel(label, new() { Exact = true })).ToBeVisibleAsync();
        }
    }

    public async Task AssertSummaryAsync(string name, int quantity, decimal total)
    {
        var summary = _page.Locator(".checkout-summary");
        await Expect(summary).ToContainTextAsync(name);
        await Expect(summary).ToContainTextAsync($"{quantity} ");
        await Expect(summary).ToContainTextAsync($"${total:F2}");
    }

    public Task BackToCartAsync() => _page.GetByRole(AriaRole.Link, new() { Name = "Back to cart", Exact = true }).ClickAsync();

    public async Task FillShippingAsync(IReadOnlyDictionary<string, string> data, string? missing = null)
    {
        foreach (var (label, value) in data)
        {
            await _page.GetByLabel(label, new() { Exact = true }).FillAsync(label == missing ? "" : value);
        }
    }

    public Task PlaceOrderAsync() => _page.GetByRole(AriaRole.Button, new() { Name = "Place order", Exact = true }).ClickAsync();

    public async Task AssertFieldValidationAsync(string label)
    {
        Assert.That(_page.Url, Is.EqualTo(TestSettings.BaseUrl + "/checkout"));
        var field = _page.Locator(FieldIds[label]);
        await Expect(field).ToBeVisibleAsync();
        Assert.That(await field.EvaluateAsync<bool>("element => element.validity.valid"), Is.False);
        Assert.That(await field.EvaluateAsync<string>("element => element.validationMessage"), Is.Not.Empty);
    }

    public Task AssertCheckoutUrlAsync() => Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/checkout");

    public async Task AssertConfirmationAsync()
    {
        var regex = new Regex(@"/orders/\d+/confirmation$");
        await Expect(_page).ToHaveURLAsync(regex);
        var match = Regex.Match(_page.Url, @"/orders/(\d+)/confirmation$");
        Assert.That(match.Success, Is.True);
        OrderId = int.Parse(match.Groups[1].Value);
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Your order was placed successfully", Exact = true })).ToBeVisibleAsync();
    }

    public Task AssertOrderNumberAsync() => Expect(_page.Locator(".confirmation > .eyebrow")).ToHaveTextAsync(new Regex(@"Order #\d+"));
    public Task AssertSuccessAsync() => Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Your order was placed successfully", Exact = true })).ToBeVisibleAsync();

    public async Task AssertOrderItemsAsync(IEnumerable<OrderItemRecord> expected)
    {
        foreach (var item in expected)
        {
            var line = _page.Locator(".confirmation .summary-lines li").Filter(new() { HasText = item.ProductName });
            await Expect(line).ToContainTextAsync(item.Quantity.ToString());
            await Expect(line).ToContainTextAsync($"${item.UnitPrice:F2}");
            await Expect(line).ToContainTextAsync($"${item.LineTotal:F2}");
        }
    }

    public Task AssertOrderTotalAsync(decimal total) => Expect(_page.Locator(".confirmation .summary-total")).ToContainTextAsync($"${total:F2}");

    public async Task AssertShippingSummaryAsync(IReadOnlyDictionary<string, string> data)
    {
        var summary = _page.Locator("[aria-labelledby=\"delivery-title\"]");
        foreach (var value in data.Values)
        {
            await Expect(summary).ToContainTextAsync(value);
        }
    }

    public Task BackToStorefrontAsync() => _page.GetByRole(AriaRole.Link, new() { Name = "Back to storefront", Exact = true }).ClickAsync();

    public async Task AssertStorefrontCatalogAsync()
    {
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Welcome to FictoShop" })).ToBeVisibleAsync();
        await Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Our products" })).ToBeVisibleAsync();
    }

    public Task AssertInsufficientStockAsync(string name) => Expect(_page.Locator(".form-error")).ToContainTextAsync($"There is no longer enough stock for {name}.");

    public async Task<(int Status, string Body)> OpenConfirmationInAnotherSessionAsync()
    {
        var browser = _page.Context.Browser ?? throw new InvalidOperationException("The current page has no browser.");
        await using var context = await browser.NewContextAsync();
        var otherPage = await context.NewPageAsync();
        var response = await otherPage.GotoAsync(_page.Url) ?? throw new InvalidOperationException("Confirmation navigation returned no response.");
        return (response.Status, await response.TextAsync());
    }
}
