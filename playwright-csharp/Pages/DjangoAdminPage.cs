using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class DjangoAdminPage
{
    private readonly IPage _page;
    private readonly ILocator _username;
    private readonly ILocator _password;
    private readonly ILocator _login;

    public DjangoAdminPage(IPage page)
    {
        _page = page;
        _username = page.GetByLabel("Username");
        _password = page.GetByLabel("Password");
        _login = page.GetByRole(AriaRole.Button, new() { Name = "Log in" });
    }

    public Task OpenAsync() => _page.GotoAsync(TestSettings.BaseUrl + "/admin/");

    public async Task LoginAsync(Credentials credentials)
    {
        await _username.FillAsync(credentials.Username);
        await _password.FillAsync(credentials.Password);
        await _login.ClickAsync();
    }

    public async Task AssertLoginPageAsync()
    {
        await Expect(_username).ToBeVisibleAsync();
        await Expect(_password).ToBeVisibleAsync();
        await Expect(_login).ToBeVisibleAsync();
    }

    public Task AssertIndexAsync() => Expect(_page.GetByRole(AriaRole.Heading, new() { Name = "Site administration" })).ToBeVisibleAsync();

    public async Task AssertProductsAndOrdersAsync()
    {
        await Expect(_page.GetByRole(AriaRole.Link, new() { Name = "Products", Exact = true })).ToBeVisibleAsync();
        await Expect(_page.GetByRole(AriaRole.Link, new() { Name = "Orders", Exact = true })).ToBeVisibleAsync();
    }

    public Task OpenNewProductAsync() => _page.GotoAsync(TestSettings.BaseUrl + "/admin/shop/product/add/");

    public async Task FillProductAsync(string name, string description, decimal price, int stock)
    {
        await _page.GetByLabel("Name:").FillAsync(name);
        await _page.GetByLabel("Description:").FillAsync(description);
        await _page.GetByLabel("Price:").FillAsync(price.ToString(System.Globalization.CultureInfo.InvariantCulture));
        await _page.GetByLabel("In stock:").FillAsync(stock.ToString());
    }

    public Task UploadImageAsync(string path) => _page.GetByLabel("Image:").SetInputFilesAsync(path);
    public Task SaveAsync() => _page.GetByRole(AriaRole.Button, new() { Name = "Save", Exact = true }).ClickAsync();
    public Task OpenProductAsync(int id) => _page.GotoAsync($"{TestSettings.BaseUrl}/admin/shop/product/{id}/change/");

    public async Task ChangeStockAsync(int stock)
    {
        await _page.GetByLabel("In stock:").FillAsync(stock.ToString());
        await SaveAsync();
    }

    public Task AssertProductListedAsync(string name) => Expect(_page.Locator("#result_list").GetByRole(AriaRole.Link, new() { Name = name, Exact = true })).ToBeVisibleAsync();
    public Task OpenOrderAsync(int id) => _page.GotoAsync($"{TestSettings.BaseUrl}/admin/shop/order/{id}/change/");

    public async Task AssertOrderAsync(OrderRecord order)
    {
        await Expect(_page.GetByLabel("Full name:")).ToHaveValueAsync(order.FullName);
        await Expect(_page.GetByLabel("Email:")).ToHaveValueAsync(order.Email);
        await Expect(_page.GetByLabel("Phone:")).ToHaveValueAsync(order.Phone);
        await Expect(_page.GetByLabel("Address:")).ToHaveValueAsync(order.Address);
        await Expect(_page.GetByLabel("Postal code:")).ToHaveValueAsync(order.PostalCode);
        await Expect(_page.GetByLabel("City:")).ToHaveValueAsync(order.City);
        await Expect(_page.GetByLabel("Country:")).ToHaveValueAsync(order.Country);
        await Expect(_page.Locator("#content-main")).ToContainTextAsync(order.TotalAmount.ToString());
        await Expect(_page.Locator(".field-created_at .readonly")).Not.ToBeEmptyAsync();
    }

    public async Task AssertItemsReadOnlyAsync(IReadOnlyList<OrderItemRecord> items)
    {
        var group = _page.Locator("#items-group");
        foreach (var item in items)
        {
            await Expect(group).ToContainTextAsync(item.ProductName);
            await Expect(group).ToContainTextAsync(item.UnitPrice.ToString());
            await Expect(group).ToContainTextAsync(item.Quantity.ToString());
            await Expect(group).ToContainTextAsync(item.LineTotal.ToString());
        }

        foreach (var field in new[] { "product_name", "unit_price", "quantity", "line_total" })
        {
            await Expect(group.Locator($"input[name$=\"-{field}\"]")).ToHaveCountAsync(0);
        }
    }
}
