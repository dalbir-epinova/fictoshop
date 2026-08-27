using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "storefront")]
public sealed class StorefrontParitySteps
{
    private readonly DjangoTestData _data;
    private readonly ScenarioState _state;
    private readonly CatalogPage _catalog;

    public StorefrontParitySteps(ScenarioContext context)
    {
        _data = context.Get<DjangoTestData>();
        _state = context.Get<ScenarioState>();
        _catalog = new CatalogPage(context.Get<Microsoft.Playwright.IPage>());
    }

    [Given("the catalog contains available and unavailable products")]
    public async Task GivenMixedCatalog()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        _state.Products["available"] = await _data.CreateProductAsync($"In-stock catalog item {reference}", "Available product for storefront tests.", 40m, 4);
        _state.Products["secondary"] = await _data.CreateProductAsync($"Secondary catalog {reference}", $"Unique storefront description {reference}", 15.50m, 9);
        _state.Products["unavailable"] = await _data.CreateProductAsync($"Sold-out catalog item {reference}", "Out-of-stock product for storefront tests.", 75m, 0);
        _state.SearchQuery = $"Unique storefront description {reference}";
    }

    [Then("the heading \"Welcome to FictoShop\" is visible")]
    [Then("the catalog is visible")]
    [Then("at least one product card is displayed")]
    public Task ThenCoreVisible() => _catalog.AssertHeadingAndCatalogAsync();

    [Then("each product card shows its name")]
    [Then("each product card shows its price")]
    [Then("each product card shows its stock status")]
    public Task ThenCardsShowInfo() => _catalog.AssertCardsHavePurchasingInformationAsync();

    [Then("an available product has an enabled \"Add to cart\" button")]
    public Task ThenAvailableAddEnabled() => _catalog.AssertAvailableAddEnabledAsync(Product("available").Name);

    [When("the customer selects a product name")]
    public Task WhenSelectsProduct() => _catalog.OpenProductAsync(Product("available").Name);

    [Then("the product detail page opens")]
    [Then("the product name, description, price, rating summary, and reviews section are visible")]
    public Task ThenProductDetails() => _catalog.AssertProductDetailAsync(Product("available"));

    [When("the customer searches for part of a product name")]
    public async Task WhenSearchesName()
    {
        _state.InitialProductCount = await _catalog.ProductCards.CountAsync();
        await _catalog.SearchAsync(Product("available").Name);
    }

    [Then("only matching products are displayed")]
    public Task ThenOnlyMatching() => _catalog.AssertOnlyProductAsync(Product("available").Name);

    [Then("the catalog status shows the number of matches")]
    public Task ThenMatchCount() => _catalog.AssertCatalogStatusAsync(1, _state.InitialProductCount);

    [When("the customer searches for text found only in a product description")]
    public Task WhenSearchesDescription() => _catalog.SearchAsync(_state.SearchQuery);

    [Then("the matching product is displayed")]
    public Task ThenDescriptionProduct() => _catalog.AssertOnlyProductAsync(Product("secondary").Name);

    [When("the customer searches for text that is not in the catalog")]
    public Task WhenNoMatchSearch() => _catalog.SearchAsync("no-such-product-playwright-9f31");

    [Then("no product cards are displayed")]
    [Then("the empty search message is visible")]
    public Task ThenNoProducts() => _catalog.AssertNoProductsAsync();

    [Given("the customer has filtered the catalog using search")]
    public async Task GivenFilteredCatalog()
    {
        _state.InitialProductCount = await _catalog.ProductCards.CountAsync();
        await _catalog.SearchAsync(Product("available").Name);
    }

    [When("the customer clears the search field")]
    public Task WhenClearsSearch() => _catalog.ClearSearchAsync();

    [Then("all products are displayed again")]
    public Task ThenAllProducts() => _catalog.AssertProductCountAsync(_state.InitialProductCount);

    [When("the customer selects \"Price: Low to high\"")]
    public Task WhenSortLow() => _catalog.SelectSortAsync("Price: Low to high");

    [Then("product prices are ordered from lowest to highest")]
    public async Task ThenPricesAscending()
    {
        var values = await _catalog.DisplayedPricesAsync();
        Assert.That(values, Is.Ordered.Ascending);
    }

    [When("the customer selects \"Price: High to low\"")]
    public Task WhenSortHigh() => _catalog.SelectSortAsync("Price: High to low");

    [Then("product prices are ordered from highest to lowest")]
    public async Task ThenPricesDescending()
    {
        var values = await _catalog.DisplayedPricesAsync();
        Assert.That(values, Is.Ordered.Descending);
    }

    [When("the customer selects \"Stock level\"")]
    public Task WhenSortStock() => _catalog.SelectSortAsync("Stock level");

    [Then("products are ordered from highest to lowest available stock")]
    public async Task ThenStocksDescending()
    {
        var values = await _catalog.DisplayedStocksAsync();
        Assert.That(values, Is.Ordered.Descending);
    }

    [When("the customer enables \"In stock only\"")]
    public Task WhenStockOnly() => _catalog.EnableInStockOnlyAsync();

    [Then("products with zero available stock are hidden")]
    public Task ThenZeroHidden() => _catalog.AssertProductHiddenAsync(Product("unavailable").Name);

    [Then("an out-of-stock product shows \"Out of stock\"")]
    [Then("its quantity controls are disabled")]
    [Then("its \"Add to cart\" button is disabled")]
    public Task ThenOutOfStockDisabled() => _catalog.AssertOutOfStockControlsAsync(Product("unavailable").Name);

    [When("the customer decreases the initial quantity")]
    public Task WhenDecreasesQuantity() => _catalog.DecreaseInitialQuantityAsync(Product("available").Name);

    [Then("the quantity remains 1")]
    public Task ThenQuantityOne() => _catalog.AssertQuantityAsync(Product("available").Name, 1);

    [When("the customer increases the quantity beyond available stock")]
    public Task WhenIncreasesBeyondStock() => _catalog.IncreaseBeyondStockAsync(Product("available").Name, Product("available").InStock);

    [Then("the quantity does not exceed available stock")]
    public Task ThenQuantityCapped() => _catalog.AssertQuantityAsync(Product("available").Name, Product("available").InStock);

    [When("the customer selects \"Explore the API\"")]
    public Task WhenExploreApi() => _catalog.ExploreApiAsync();

    [Then("the browser opens the \"\\/products\" endpoint")]
    public Task ThenProductsEndpoint() => _catalog.AssertProductsEndpointAsync();

    [Then("the response contains catalog products")]
    public Task ThenApiProducts() => _catalog.AssertApiCatalogProductsAsync();

    private ProductRecord Product(string key) => _state.Products[key];
}
