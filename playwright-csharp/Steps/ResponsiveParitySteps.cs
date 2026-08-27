using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "responsive")]
public sealed class ResponsiveParitySteps
{
    private readonly DjangoTestData _data;
    private readonly ScenarioState _state;
    private readonly ShoppingCartPage _cart;
    private readonly OrderCheckoutPage _checkout;
    private readonly MobilePage _mobile;

    public ResponsiveParitySteps(ScenarioContext context)
    {
        _data = context.Get<DjangoTestData>();
        _state = context.Get<ScenarioState>();
        var page = context.Get<Microsoft.Playwright.IPage>();
        _cart = new ShoppingCartPage(page);
        _checkout = new OrderCheckoutPage(page);
        _mobile = new MobilePage(page, _state);
    }

    [Given("the browser viewport is {string}")]
    public Task GivenViewport(string viewport)
    {
        var values = viewport.ToLowerInvariant().Split('x').Select(value => int.Parse(value.Trim())).ToArray();
        return _mobile.SetViewportAsync(values[0], values[1]);
    }

    [Given("the browser uses a mobile viewport")]
    public Task GivenMobileViewport() => _mobile.SetViewportAsync(390, 844);

    [Then("the heading and catalog fit within the viewport")]
    public Task ThenStorefrontFits() => _mobile.AssertStorefrontFitsAsync();

    [Then("primary controls are usable without horizontal scrolling")]
    public Task ThenControlsUsable() => _mobile.AssertPrimaryControlsAsync();

    [When("the customer adds a product to the cart")]
    public async Task WhenAddsProduct()
    {
        await EnsureProductAsync();
        await _cart.OpenAsync();
        await _cart.AddProductAsync(Product.Name, 1);
    }

    [Then("the entire floating cart width remains inside the viewport")]
    public Task ThenCartWidth() => _mobile.AssertCartWidthAsync();

    [Then("the cart lines can scroll when their content exceeds the maximum height")]
    public Task ThenLinesScrollable() => _mobile.AssertCartLinesScrollableAsync();

    [Then("\"Clear\" and \"Checkout\" remain usable")]
    public Task ThenCartActions() => _mobile.AssertCartActionsAsync();

    [Given("the cart contains a product")]
    public async Task GivenCartProduct()
    {
        await EnsureProductAsync();
        await _cart.OpenAsync();
        await _cart.AddProductAsync(Product.Name, 1);
    }

    [When("the customer opens checkout")]
    public Task WhenOpensCheckout() => _checkout.OpenAsync();

    [Then("shipping fields are arranged in one column")]
    public Task ThenSingleColumn() => _mobile.AssertCheckoutSingleColumnAsync();

    [Then("\"Back to cart\" and \"Place order\" are usable")]
    public Task ThenCheckoutActions() => _mobile.AssertCheckoutActionsAsync();

    [Given("the storefront is running in an Android emulator")]
    public void GivenAndroidBundle()
    {
        Assert.That(File.Exists(Path.Combine(ProjectPaths.Root, "android-app", "app", "src", "main", "assets", "index.html")), Is.True);
        _state.SelectedProductName = "android";
    }

    [Given("the storefront is running in the iOS app")]
    public void GivenIosBundle()
    {
        Assert.That(File.Exists(Path.Combine(ProjectPaths.Root, "ios-app", "fictoshop", "fictoshop", "WebView.swift")), Is.True);
        _state.SelectedProductName = "ios";
    }

    [When("the mobile bundle requests products")]
    public Task WhenBundleRequests() => _state.SelectedProductName == "android" ? _mobile.LoadAndroidBundleAsync() : _mobile.LoadIosBundleAsync();

    [Then("it uses \"http:\\/\\/10.0.2.2:8000\"")]
    public void ThenAndroidBase() => _mobile.AssertAndroidBase();

    [Then("it uses the configured \"API_BASE_URL\"")]
    public void ThenIosBase() => _mobile.AssertIosBase();

    [Then("catalog products are displayed")]
    public Task ThenProductsDisplayed() => _mobile.AssertBundleProductAsync();

    private ProductRecord Product => _state.Products["mobile"];

    private async Task EnsureProductAsync()
    {
        if (!_state.Products.ContainsKey("mobile"))
        {
            var reference = Guid.NewGuid().ToString("N")[..8];
            _state.Products["mobile"] = await _data.CreateProductAsync($"Mobile product {reference}", "Product for mobile layout tests.", 49.95m, 7);
        }
    }
}
