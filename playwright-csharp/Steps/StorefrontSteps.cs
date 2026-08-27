using Fictoshop.PlaywrightTests.Pages;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
public sealed class StorefrontSteps
{
    private readonly ScenarioContext _scenarioContext;
    private readonly StorefrontPage _storefront;

    public StorefrontSteps(ScenarioContext scenarioContext)
    {
        _scenarioContext = scenarioContext;
        _storefront = scenarioContext.Get<StorefrontPage>();
    }

    [Given("the customer opens the storefront")]
    public Task GivenTheCustomerOpensTheStorefront() => _storefront.OpenAsync();

    [Then("the heading, catalog, and products are visible")]
    public Task ThenTheHeadingCatalogAndProductsAreVisible() =>
        _storefront.AssertCatalogIsVisibleAsync();

    [When("the customer searches for the first product")]
    public async Task WhenTheCustomerSearchesForTheFirstProduct()
    {
        _scenarioContext["SelectedProduct"] = await _storefront.SearchForFirstProductAsync();
    }

    [Then("only that product is displayed")]
    public Task ThenOnlyThatProductIsDisplayed() =>
        _storefront.AssertOnlyProductIsVisibleAsync(SelectedProduct);

    [When("the customer opens the first product")]
    public async Task WhenTheCustomerOpensTheFirstProduct()
    {
        _scenarioContext["SelectedProduct"] = await _storefront.OpenFirstProductAsync();
    }

    [Then("the product details and reviews section are visible")]
    public Task ThenTheProductDetailsAndReviewsSectionAreVisible() =>
        _storefront.AssertProductDetailsAsync(SelectedProduct);

    [When("the customer adds the first available product to the cart")]
    public async Task WhenTheCustomerAddsTheFirstAvailableProductToTheCart()
    {
        _scenarioContext["SelectedProduct"] = await _storefront.AddFirstAvailableProductAsync();
    }

    [Then("the cart contains that product and one item")]
    public Task ThenTheCartContainsThatProductAndOneItem() =>
        _storefront.AssertCartContainsAsync(SelectedProduct);

    private string SelectedProduct => _scenarioContext.Get<string>("SelectedProduct");
}
