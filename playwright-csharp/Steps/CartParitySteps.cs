using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "cart")]
public sealed class CartParitySteps
{
    private readonly DjangoTestData _data;
    private readonly StorefrontApi _api;
    private readonly ScenarioState _state;
    private readonly ShoppingCartPage _cart;

    public CartParitySteps(ScenarioContext context)
    {
        _data = context.Get<DjangoTestData>();
        _api = context.Get<StorefrontApi>();
        _state = context.Get<ScenarioState>();
        _cart = new ShoppingCartPage(context.Get<Microsoft.Playwright.IPage>());
    }

    [Given("the cart has been cleared")]
    public async Task GivenCartCleared() => Assert.That((await _api.DeleteAsync("/cart")).IsSuccess, Is.True);

    [Given("the catalog contains an available product")]
    public async Task GivenAvailableProduct()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        _state.Products["primary"] = await _data.CreateProductAsync($"Playwright product {reference}", "Product created for C# cart scenarios.", 49.95m, 7);
        _state.Products["secondary"] = await _data.CreateProductAsync($"Second cart product {reference}", "Second product for C# cart scenarios.", 15.25m, 8);
    }

    [Then("the floating cart is not visible")]
    [Then("the floating cart is hidden")]
    public Task ThenCartHidden() => _cart.AssertHiddenAsync();

    [When("the customer adds 1 available product to the cart")]
    public Task WhenAddsOne() => _cart.AddProductAsync(Primary.Name);

    [Then("the floating cart is visible")]
    public Task ThenCartVisible() => _cart.AssertVisibleAsync();

    [Then("it shows the product name")]
    public Task ThenNameShown() => _cart.AssertProductInCartAsync(Primary.Name);

    [Then("it shows 1 total item")]
    public Task ThenOneItem() => _cart.AssertTotalItemsAsync(1);

    [Then("it shows the correct total price")]
    public Task ThenCorrectTotal() => _cart.AssertGrandTotalAsync(Primary.Price);

    [Given("the customer has added a product to the cart")]
    [Given("the customer has added 1 product to the cart")]
    public Task GivenAddedProduct() => _cart.AddProductAsync(Primary.Name);

    [When("the customer scrolls to another part of the storefront")]
    public Task WhenScrolls() => _cart.ScrollAsync();

    [Then("the floating cart remains inside the viewport")]
    public Task ThenInsideViewport() => _cart.AssertInsideViewportAsync();

    [When("the customer selects quantity 3")]
    public Task WhenSelectsThree() => _cart.SelectQuantityAsync(Primary.Name, 3);

    [When("adds the product to the cart")]
    public Task WhenAddsSelected() => _cart.AddSelectedProductAsync(Primary.Name);

    [Then("the cart line shows quantity 3")]
    [Then("the line quantity is 3")]
    public Task ThenLineThree() => _cart.AssertLineQuantityAsync(Primary.Name, 3);

    [Then("the total equals three times the unit price")]
    public Task ThenTotalThree() => _cart.AssertGrandTotalAsync(Primary.Price * 3);

    [When("the customer adds 2 more of the same product")]
    public Task WhenAddsTwoMore() => _cart.AddProductAsync(Primary.Name, 2);

    [Then("the cart contains one line for that product")]
    public Task ThenOneLine() => _cart.AssertOneLineAsync(Primary.Name);

    [When("the customer adds multiple different products")]
    [Given("the cart contains two different products")]
    [Given("the cart contains products")]
    public async Task GivenOrWhenMultiple()
    {
        await _cart.AddProductAsync(Primary.Name, 1);
        await _cart.AddProductAsync(Secondary.Name, 2);
    }

    [Then("every selected product is shown in the cart")]
    public async Task ThenAllShown()
    {
        await _cart.AssertProductInCartAsync(Primary.Name);
        await _cart.AssertProductInCartAsync(Secondary.Name);
    }

    [Then("total items equal the sum of all quantities")]
    public Task ThenTotalItemsThree() => _cart.AssertTotalItemsAsync(3);

    [Then("the grand total equals the sum of all line totals")]
    public Task ThenGrandTotal() => _cart.AssertGrandTotalAsync(Primary.Price + Secondary.Price * 2);

    [When("the customer removes one product")]
    public Task WhenRemovesOne() => _cart.RemoveProductAsync(Primary.Name);

    [Then("only that product disappears from the cart")]
    public async Task ThenOnlyRemovedDisappears()
    {
        await _cart.AssertProductNotInCartAsync(Primary.Name);
        await _cart.AssertProductInCartAsync(Secondary.Name);
    }

    [Then("the totals are recalculated")]
    public async Task ThenTotalsRecalculated()
    {
        await _cart.AssertTotalItemsAsync(2);
        await _cart.AssertGrandTotalAsync(Secondary.Price * 2);
    }

    [When("the customer selects \"Clear\"")]
    public Task WhenClears() => _cart.ClearAsync();

    [Then("all cart lines are removed")]
    public async Task ThenLinesRemoved() => Assert.That(await _cart.CartItems.CountAsync(), Is.Zero);

    [When("the customer reloads the storefront")]
    public Task WhenReloads() => _cart.ReloadAsync();

    [Then("the same product and quantity remain in the cart")]
    public async Task ThenCartPersists()
    {
        await _cart.AssertProductInCartAsync(Primary.Name);
        await _cart.AssertLineQuantityAsync(Primary.Name, 1);
    }

    [When("the customer attempts to add more units than available")]
    public Task WhenOverStock() => _cart.AttemptOverStockAsync(Primary.Name, Primary.InStock);

    [Then("the request is rejected")]
    public void ThenRejected() => _cart.AssertRequestRejected();

    [Then("a stock error is displayed")]
    public Task ThenStockError() => _cart.AssertStockErrorAsync(Primary.InStock, Primary.Name);

    [Then("the cart quantity is unchanged")]
    public Task ThenCartUnchanged() => _cart.AssertTotalItemsAsync(0);

    [When("the customer removes that product from the cart")]
    public Task WhenRemovesProduct() => _cart.RemoveProductAsync(Primary.Name);

    [Then("the catalog shows the original available stock")]
    public Task ThenOriginalStock() => _cart.AssertCatalogStockAsync(Primary.Name, Primary.InStock);

    private ProductRecord Primary => _state.Products["primary"];
    private ProductRecord Secondary => _state.Products["secondary"];
}
