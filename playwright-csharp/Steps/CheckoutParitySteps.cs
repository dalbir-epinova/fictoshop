using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "checkout")]
public sealed class CheckoutParitySteps
{
    private readonly IPage _page;
    private readonly DjangoTestData _data;
    private readonly StorefrontApi _api;
    private readonly ScenarioState _state;
    private readonly ShoppingCartPage _cart;
    private readonly OrderCheckoutPage _checkout;

    public CheckoutParitySteps(ScenarioContext context)
    {
        _page = context.Get<IPage>();
        _data = context.Get<DjangoTestData>();
        _api = context.Get<StorefrontApi>();
        _state = context.Get<ScenarioState>();
        _cart = new ShoppingCartPage(_page);
        _checkout = new OrderCheckoutPage(_page);
    }

    [Given("an available product exists")]
    public async Task GivenAvailableProduct()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        _state.Products["available"] = await _data.CreateProductAsync($"Checkout product {reference}", "Product for C# checkout scenarios.", 49.95m, 7);
        _state.InitialStock = Available.InStock;
        _state.InitialOrderCount = await _data.CountOrdersAsync();
        _state.Shipping = ShippingData(reference);
        await _api.DeleteAsync("/cart");
    }

    [When("the customer opens \"\\/checkout\" with an empty cart")]
    public Task WhenOpensEmptyCheckout() => _checkout.OpenAsync();

    [Then("the customer is redirected to the storefront")]
    public Task ThenRedirected() => _checkout.AssertStorefrontAsync();

    [Given("the customer has added a product to the cart")]
    public async Task GivenAddedProduct()
    {
        await _cart.OpenAsync();
        await _cart.AddProductAsync(Available.Name, 1);
    }

    [When("the customer selects \"Checkout\"")]
    public Task WhenSelectsCheckout() => _page.GetByRole(AriaRole.Button, new() { Name = "Checkout", Exact = true }).ClickAsync();

    [Then("the shipping details page opens")]
    public Task ThenShippingPage() => _checkout.AssertShippingPageAsync();

    [Then("fields for name, email, phone, address, postal code, city, and country are visible")]
    public Task ThenShippingFields() => _checkout.AssertShippingFieldsAsync();

    [Then("the ordered product, quantity, and total are visible")]
    public Task ThenSummary() => _checkout.AssertSummaryAsync(Available.Name, 1, Available.Price);

    [Given("the customer is on checkout with a product in the cart")]
    public async Task GivenOnCheckout()
    {
        await _cart.OpenAsync();
        await _cart.AddProductAsync(Available.Name, 1);
        await _checkout.OpenAsync();
    }

    [When("the customer selects \"Back to cart\"")]
    public Task WhenBackToCart() => _checkout.BackToCartAsync();

    [Then("the storefront opens at the cart")]
    public void ThenStorefrontAtCart() => Assert.That(_page.Url, Is.EqualTo(TestSettings.BaseUrl + "/#cart"));

    [Then("the product remains in the cart")]
    public Task ThenProductRemains() => _cart.AssertProductInCartAsync(Available.Name);

    [When("the customer submits valid shipping details except for {string}")]
    public async Task WhenSubmitsMissing(string field)
    {
        await _checkout.FillShippingAsync(_state.Shipping, field);
        await _checkout.PlaceOrderAsync();
    }

    [Then("the order is not placed")]
    [Then("no order is created")]
    public async Task ThenNoOrder() => Assert.That(await _data.CountOrdersAsync(), Is.EqualTo(_state.InitialOrderCount));

    [Then("a validation message is shown for {string}")]
    public Task ThenFieldValidation(string field) => _checkout.AssertFieldValidationAsync(field);

    [When("the customer enters an invalid email address")]
    public async Task WhenInvalidEmail()
    {
        var invalid = new Dictionary<string, string>(_state.Shipping) { ["Email"] = "invalid-email" };
        await _checkout.FillShippingAsync(invalid);
    }

    [When("attempts to place the order")]
    public Task WhenAttemptsOrder() => _checkout.PlaceOrderAsync();

    [Then("the email field reports a validation error")]
    public Task ThenEmailValidation() => _checkout.AssertFieldValidationAsync("Email");

    [When("the customer enters valid shipping details")]
    public Task WhenValidShipping() => _checkout.FillShippingAsync(_state.Shipping);

    [When("selects \"Place order\"")]
    public Task WhenPlaceOrder() => _checkout.PlaceOrderAsync();

    [Then("an order confirmation page opens")]
    public Task ThenConfirmation() => _checkout.AssertConfirmationAsync();

    [Then("a unique order number is displayed")]
    public Task ThenOrderNumber() => _checkout.AssertOrderNumberAsync();

    [Then("the page confirms that the order was placed successfully")]
    public Task ThenSuccess() => _checkout.AssertSuccessAsync();

    [When("the customer places a valid order containing multiple products")]
    public async Task WhenMultipleOrder()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        _state.Products["secondary"] = await _data.CreateProductAsync($"Checkout second {reference}", "Checkout test product", 12.50m, 6);
        await PlaceOrderAsync((Available, 1), (Secondary, 2));
    }

    [Then("every product name, unit price, quantity, and line total is shown")]
    public Task ThenAllItemDetails() => _checkout.AssertOrderItemsAsync(_state.ExpectedItems);

    [Then("the correct order total is shown")]
    public Task ThenCorrectOrderTotal() => _checkout.AssertOrderTotalAsync(_state.ExpectedItems.Sum(item => item.LineTotal));

    [When("the customer places an order with valid shipping details")]
    [When("the customer places a valid order")]
    public Task WhenValidOrder() => PlaceOrderAsync((Available, 2));

    [Then("the confirmation shows the customer's name")]
    public Task ThenCustomerName() => _checkout.AssertShippingSummaryAsync(SelectShipping("Full name"));

    [Then("it shows the address, postal code, city, and country")]
    public Task ThenAddress() => _checkout.AssertShippingSummaryAsync(SelectShipping("Address", "Postal code", "City", "Country"));

    [Then("it shows the email and phone number")]
    public Task ThenContact() => _checkout.AssertShippingSummaryAsync(SelectShipping("Email", "Phone"));

    [When("returns to the storefront")]
    public Task WhenReturns() => _checkout.BackToStorefrontAsync();

    [Then("the floating cart is hidden")]
    public Task ThenCartHidden() => _cart.AssertHiddenAsync();

    [Then("product stock is reduced by the purchased quantity")]
    public Task ThenStockReduced() => _cart.AssertCatalogStockAsync(Available.Name, _state.InitialStock - 2);

    [Given("the customer has placed an order")]
    public Task GivenPlacedOrder() => PlaceOrderAsync((Available, 1));

    [When("the customer selects \"Back to storefront\"")]
    public Task WhenBackToStorefront() => _checkout.BackToStorefrontAsync();

    [Then("the storefront heading and catalog are visible")]
    public Task ThenStorefrontCatalog() => _checkout.AssertStorefrontCatalogAsync();

    [Given("a customer has placed an order in one browser session")]
    public Task GivenOrderOneSession() => PlaceOrderAsync((Available, 1));

    [When("a different browser session opens that confirmation URL")]
    public async Task WhenDifferentSession()
    {
        var result = await _checkout.OpenConfirmationInAnotherSessionAsync();
        _state.LastBrowserStatus = result.Status;
        _state.LastBrowserBody = result.Body;
    }

    [Then("a 404 response is returned")]
    public void Then404() => Assert.That(_state.LastBrowserStatus, Is.EqualTo(404));

    [Then("no customer or shipping details are exposed")]
    public void ThenNoDetails()
    {
        foreach (var value in _state.Shipping.Values)
        {
            Assert.That(_state.LastBrowserBody, Does.Not.Contain(value));
        }
    }

    [Given("the customer has products in the cart")]
    public async Task GivenProductsInCart()
    {
        await _cart.OpenAsync();
        await _cart.AddProductAsync(Available.Name, 2);
        await _checkout.OpenAsync();
    }

    [Given("one product no longer has enough stock")]
    public async Task GivenStockChanged()
    {
        await _data.SetProductStockAsync(Available.Id, 1);
        _state.InitialStock = 1;
    }

    [When("the customer submits valid shipping details")]
    public async Task WhenSubmitsValidShipping()
    {
        await _checkout.FillShippingAsync(_state.Shipping);
        await _checkout.PlaceOrderAsync();
    }

    [Then("an insufficient-stock message identifies the product")]
    public Task ThenInsufficientMessage() => _checkout.AssertInsufficientStockAsync(Available.Name);

    [Then("no product stock is reduced")]
    public async Task ThenNoStockReduced() => Assert.That(await _data.GetProductStockAsync(Available.Id), Is.EqualTo(_state.InitialStock));

    [Then("the cart remains unchanged")]
    public async Task ThenCartUnchanged() => Assert.That((await _api.GetAsync("/cart")).Json.GetProperty("total_items").GetInt32(), Is.EqualTo(2));

    private async Task PlaceOrderAsync(params (ProductRecord Product, int Quantity)[] products)
    {
        _state.ExpectedItems.Clear();
        await _cart.OpenAsync();
        foreach (var (product, quantity) in products)
        {
            await _cart.AddProductAsync(product.Name, quantity);
            _state.ExpectedItems.Add(new OrderItemRecord(product.Name, product.Price, quantity, product.Price * quantity));
        }
        await _checkout.OpenAsync();
        await _checkout.FillShippingAsync(_state.Shipping);
        await _checkout.PlaceOrderAsync();
        await _checkout.AssertConfirmationAsync();
    }

    private Dictionary<string, string> SelectShipping(params string[] keys) => keys.ToDictionary(key => key, key => _state.Shipping[key]);
    private ProductRecord Available => _state.Products["available"];
    private ProductRecord Secondary => _state.Products["secondary"];

    private static Dictionary<string, string> ShippingData(string reference) => new()
    {
        ["Full name"] = $"Checkout Customer {reference}",
        ["Email"] = $"checkout-{reference}@example.com",
        ["Phone"] = "+47 99887766",
        ["Address"] = "Testveien 42",
        ["Postal code"] = "0123",
        ["City"] = "Oslo",
        ["Country"] = "Norway",
    };
}
