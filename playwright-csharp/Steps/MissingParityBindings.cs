using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using Reqnroll;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "checkout")]
public sealed class CheckoutBackgroundBindings
{
    private readonly StorefrontApi _api;

    public CheckoutBackgroundBindings(ScenarioContext context)
    {
        _api = context.Get<StorefrontApi>();
    }

    [Given("the cart has been cleared")]
    public async Task GivenCartCleared() => Assert.That((await _api.DeleteAsync("/cart")).IsSuccess, Is.True);
}

[Binding]
[Scope(Tag = "responsive")]
public sealed class ResponsiveNavigationBindings
{
    private readonly ShoppingCartPage _cart;

    public ResponsiveNavigationBindings(ScenarioContext context)
    {
        _cart = new ShoppingCartPage(context.Get<IPage>());
    }

    [When("the customer opens the storefront")]
    public Task WhenStorefrontOpens() => _cart.OpenAsync();
}

[Binding]
[Scope(Tag = "authentication")]
public sealed class LogoutBindings
{
    private readonly IPage _page;

    public LogoutBindings(ScenarioContext context)
    {
        _page = context.Get<IPage>();
    }

    [When("the user selects \"Log out\"")]
    public Task WhenLogout() => _page.Locator("header").GetByRole(AriaRole.Button, new() { Name = "Log out", Exact = true }).ClickAsync();

    [Then("the navigation shows \"Log in\"")]
    public Task ThenLoginShown() => Expect(_page.Locator("header").GetByRole(AriaRole.Link, new() { Name = "Log in", Exact = true })).ToBeVisibleAsync();
}

[Binding]
[Scope(Tag = "api")]
public sealed class ApiStatusBindings
{
    private readonly ScenarioState _state;

    public ApiStatusBindings(ScenarioContext context)
    {
        _state = context.Get<ScenarioState>();
    }

    [Then("the API returns status {int}")]
    public void ThenStatus(int status)
    {
        var response = _state.Response ?? throw new InvalidOperationException("API response is missing.");
        Assert.That((int)response.Status, Is.EqualTo(status), response.Text);
    }
}
