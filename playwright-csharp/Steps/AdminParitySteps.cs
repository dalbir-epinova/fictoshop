using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "admin")]
public sealed class AdminParitySteps
{
    private readonly IPage _page;
    private readonly DjangoTestData _data;
    private readonly ScenarioState _state;
    private readonly DjangoAdminPage _admin;
    private readonly CatalogPage _catalog;
    private readonly string _productName = $"Playwright product {Guid.NewGuid().ToString("N")[..8]}";
    private const string Description = "Product created by the Playwright admin scenario.";
    private const decimal Price = 49.95m;
    private const int Stock = 7;
    private const int NewStock = 12;

    public AdminParitySteps(ScenarioContext context)
    {
        _page = context.Get<IPage>();
        _data = context.Get<DjangoTestData>();
        _state = context.Get<ScenarioState>();
        _admin = new DjangoAdminPage(_page);
        _catalog = new CatalogPage(_page);
    }

    [Given("the customer is signed out")]
    public Task GivenSignedOut() => _page.Context.ClearCookiesAsync();

    [Given("a superuser is signed in")]
    public async Task GivenAdminSignedIn()
    {
        _state.Admin ??= await _data.CreateUserAsync(true);
        await _admin.OpenAsync();
        await _admin.LoginAsync(_state.Admin);
        await _admin.AssertIndexAsync();
    }

    [When("the customer opens \"\\/admin\\/\"")]
    [When("the superuser opens \"\\/admin\\/\"")]
    public Task WhenOpensAdmin() => _admin.OpenAsync();

    [Then("the Django admin login page is displayed")]
    public Task ThenLoginPage() => _admin.AssertLoginPageAsync();

    [Then("the administration index is visible")]
    public Task ThenAdminIndex() => _admin.AssertIndexAsync();

    [Then("Products and Orders are listed")]
    public Task ThenProductsOrders() => _admin.AssertProductsAndOrdersAsync();

    [When("the superuser opens the new product form")]
    public Task WhenNewProductForm() => _admin.OpenNewProductAsync();

    [When("enters a valid product name, description, price, and stock")]
    public Task WhenFillsProduct() => _admin.FillProductAsync(_productName, Description, Price, Stock);

    [When("uploads a dummy product image")]
    public Task WhenUploadsImage() => _admin.UploadImageAsync(Path.Combine(ProjectPaths.Root, "images", "uploads", "boxing_gloves.jpg"));

    [When("saves the product")]
    public Task WhenSavesProduct() => _admin.SaveAsync();

    [Then("the product appears in Django administration")]
    public Task ThenProductInAdmin() => _admin.AssertProductListedAsync(_productName);

    [Then("the product appears in the storefront catalog")]
    public async Task ThenProductInStorefront()
    {
        await _catalog.OpenAsync();
        await _catalog.AssertProductVisibleAsync(_productName);
    }

    [Then("the product image is displayed in the storefront catalog")]
    public Task ThenProductImage() => _catalog.AssertProductImageAsync(_productName);

    [Given("a product exists")]
    public async Task GivenProductExists() => _state.Products["admin"] = await _data.CreateProductAsync(_productName, Description, Price, Stock);

    [When("the superuser changes its stock value")]
    public async Task WhenChangesStock()
    {
        await _admin.OpenProductAsync(_state.Products["admin"].Id);
        await _admin.ChangeStockAsync(NewStock);
    }

    [Then("the new stock value appears in the storefront")]
    public async Task ThenNewStock()
    {
        await _catalog.OpenAsync();
        await _catalog.AssertProductStockAsync(_productName, NewStock);
    }

    [Given("a customer order exists")]
    public async Task GivenOrderExists() => _state.Order = await _data.CreateOrderAsync();

    [When("the superuser opens that order in administration")]
    public Task WhenOpensOrder() => _admin.OpenOrderAsync(Order.Id);

    [Then("customer, shipping, total, and creation details are visible")]
    public Task ThenOrderDetails() => _admin.AssertOrderAsync(Order);

    [Then("each order line is visible as read-only data")]
    public Task ThenLinesReadOnly() => _admin.AssertItemsReadOnlyAsync(Order.Items);

    private OrderRecord Order => _state.Order ?? throw new InvalidOperationException("Order fixture is missing.");
}
