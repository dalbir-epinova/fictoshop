using System.Net;
using Fictoshop.PlaywrightTests.Support;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "api")]
public sealed class ApiParitySteps
{
    private readonly DjangoTestData _data;
    private readonly StorefrontApi _api;
    private readonly ScenarioState _state;

    public ApiParitySteps(ScenarioContext context)
    {
        _data = context.Get<DjangoTestData>();
        _api = context.Get<StorefrontApi>();
        _state = context.Get<ScenarioState>();
    }

    [When("the client requests {string}")]
    public async Task WhenClientRequests(string path) => _state.Response = await _api.GetAsync(path);

    [Then("the response is successful")]
    public void ThenSuccessful() => Assert.That(Response.IsSuccess, Is.True, Response.Text);

    [Then("it identifies the frontend, products, cart, login, and API exploration paths")]
    public void ThenMetadataPaths()
    {
        var json = Response.Json;
        Assert.Multiple(() =>
        {
            Assert.That(json.GetProperty("frontend").GetString(), Is.EqualTo("/"));
            Assert.That(json.GetProperty("products").GetString(), Is.EqualTo("/products"));
            Assert.That(json.GetProperty("cart").GetString(), Is.EqualTo("/cart"));
            Assert.That(json.GetProperty("login").GetString(), Is.EqualTo("/login"));
            Assert.That(json.GetProperty("docs").GetString(), Is.EqualTo("/products"));
        });
    }

    [Then("each product contains id, name, description, price, stock, image, rating, and review count")]
    public void ThenProductFields()
    {
        Assert.That(Response.Json.ValueKind, Is.EqualTo(System.Text.Json.JsonValueKind.Array));
        Assert.That(Response.Json.GetArrayLength(), Is.GreaterThan(0));
        var fields = new[] { "id", "name", "description", "price", "in_stock", "image_url", "average_rating", "review_count" };
        foreach (var product in Response.Json.EnumerateArray())
        {
            foreach (var field in fields)
            {
                Assert.That(product.TryGetProperty(field, out _), Is.True, $"Product is missing {field}");
            }
        }
    }

    [Given("a product with reviews exists")]
    public async Task GivenProductWithReviews()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        var product = await _data.CreateProductAsync($"Reviewed product {reference}", "Product created for the API review scenario.", 64.50m, 9);
        _state.Products["reviewed"] = product;
        var one = await _data.CreateUserAsync(false);
        var two = await _data.CreateUserAsync(false);
        _state.ExpectedItems.Clear();
        var first = await _data.CreateReviewAsync(product, one, 4.5m, "Excellent test product.");
        var second = await _data.CreateReviewAsync(product, two, 3.5m, "Useful, with room for improvement.");
        _state.RequestedUrls.Clear();
        _state.RequestedUrls.Add($"{first.User}|{first.Rating}|{first.Comment}");
        _state.RequestedUrls.Add($"{second.User}|{second.Rating}|{second.Comment}");
    }

    [When("the client requests that product from \"\\/products\\/<id>\"")]
    public async Task WhenProductDetail() => _state.Response = await _api.GetAsync($"/products/{Product.Id}");

    [Then("the response contains the selected product")]
    public void ThenSelectedProduct()
    {
        var json = Response.Json;
        Assert.That(Response.IsSuccess, Is.True, Response.Text);
        Assert.Multiple(() =>
        {
            Assert.That(json.GetProperty("id").GetInt32(), Is.EqualTo(Product.Id));
            Assert.That(json.GetProperty("name").GetString(), Is.EqualTo(Product.Name));
            Assert.That(json.GetProperty("description").GetString(), Is.EqualTo(Product.Description));
            Assert.That(json.GetProperty("price").GetDecimal(), Is.EqualTo(Product.Price));
            Assert.That(json.GetProperty("in_stock").GetInt32(), Is.EqualTo(Product.InStock));
        });
    }

    [Then("it contains the product reviews")]
    public void ThenReviews()
    {
        var reviews = Response.Json.GetProperty("reviews").EnumerateArray().ToDictionary(item => item.GetProperty("user").GetString()!);
        Assert.That(reviews, Has.Count.EqualTo(2));
        foreach (var encoded in _state.RequestedUrls)
        {
            var parts = encoded.Split('|', 3);
            Assert.That(reviews[parts[0]].GetProperty("rating").GetString(), Is.EqualTo(decimal.Parse(parts[1]).ToString("F1")));
            Assert.That(reviews[parts[0]].GetProperty("comment").GetString(), Is.EqualTo(parts[2]));
        }
    }

    [When("the client requests an unknown product id")]
    public async Task WhenUnknownProduct() => _state.Response = await _api.GetAsync("/products/2147483647");

    [Then("the API returns status {string}")]
    public void ThenApiStatus(string status) => Assert.That((int)Response.Status, Is.EqualTo(int.Parse(status)), Response.Text);

    [Then("the response says \"Product not found\"")]
    public void ThenNotFoundMessage() => Assert.That(Response.Json.GetProperty("detail").GetString(), Is.EqualTo("Product not found"));

    [Given("an available product exists")]
    public async Task GivenAvailableProduct()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        _state.Products["available"] = await _data.CreateProductAsync($"API product {reference}", "Product for C# API scenarios.", 49.95m, 7);
        await _api.DeleteAsync("/cart");
    }

    [When("the client posts its id and a valid quantity to \"\\/cart\"")]
    public async Task WhenPostsProduct() => _state.Response = await _api.PostAsync("/cart", new { product_id = Available.Id, quantity = 2 });

    [Then("the response contains the updated items, item count, and total")]
    public void ThenUpdatedCart()
    {
        var json = Response.Json;
        var item = json.GetProperty("items")[0];
        Assert.Multiple(() =>
        {
            Assert.That(json.GetProperty("items").GetArrayLength(), Is.EqualTo(1));
            Assert.That(item.GetProperty("product").GetProperty("id").GetInt32(), Is.EqualTo(Available.Id));
            Assert.That(item.GetProperty("quantity").GetInt32(), Is.EqualTo(2));
            Assert.That(item.GetProperty("line_total").GetDecimal(), Is.EqualTo(Available.Price * 2));
            Assert.That(json.GetProperty("total_items").GetInt32(), Is.EqualTo(2));
            Assert.That(json.GetProperty("grand_total").GetDecimal(), Is.EqualTo(Available.Price * 2));
        });
    }

    [When("the client posts product id {string} and quantity {string} to \"\\/cart\"")]
    public async Task WhenPostsInvalid(string productId, string quantity)
    {
        if (!_state.Products.ContainsKey("available"))
        {
            await GivenAvailableProduct();
        }

        var resolvedId = productId switch { "valid" => Available.Id, "unknown" => 2147483647, _ => int.Parse(productId) };
        var resolvedQuantity = quantity == "too many" ? Available.InStock + 1 : int.Parse(quantity);
        _state.Response = await _api.PostAsync("/cart", new { product_id = resolvedId, quantity = resolvedQuantity });
    }

    [Given("the cart API contains a product")]
    [Given("the cart API contains products")]
    public async Task GivenCartApiContainsProduct()
    {
        await GivenAvailableProduct();
        var response = await _api.PostAsync("/cart", new { product_id = Available.Id, quantity = 2 });
        Assert.That(response.Status, Is.EqualTo(HttpStatusCode.Created));
    }

    [When("the client deletes \"\\/cart\\/<product_id>\"")]
    public async Task WhenDeletesProduct() => _state.Response = await _api.DeleteAsync($"/cart/{Available.Id}");

    [Then("that product is absent from the returned cart")]
    public void ThenProductAbsent()
    {
        Assert.That(Response.IsSuccess, Is.True, Response.Text);
        var ids = Response.Json.GetProperty("items").EnumerateArray().Select(item => item.GetProperty("product").GetProperty("id").GetInt32());
        Assert.That(ids, Does.Not.Contain(Available.Id));
        Assert.That(Response.Json.GetProperty("total_items").GetInt32(), Is.Zero);
        Assert.That(Response.Json.GetProperty("grand_total").GetDecimal(), Is.Zero);
    }

    [When("the client deletes \"\\/cart\"")]
    public async Task WhenClearsCart() => _state.Response = await _api.DeleteAsync("/cart");

    [Then("the returned cart is empty")]
    public void ThenCartEmpty()
    {
        Assert.That(Response.IsSuccess, Is.True, Response.Text);
        Assert.That(Response.Json.GetProperty("items").GetArrayLength(), Is.Zero);
    }

    [Then("total items and grand total are zero")]
    public void ThenTotalsZero()
    {
        Assert.That(Response.Json.GetProperty("total_items").GetInt32(), Is.Zero);
        Assert.That(Response.Json.GetProperty("grand_total").GetDecimal(), Is.Zero);
    }

    private ApiResponse Response => _state.Response ?? throw new InvalidOperationException("API response is missing.");
    private ProductRecord Product => _state.Products["reviewed"];
    private ProductRecord Available => _state.Products["available"];
}
