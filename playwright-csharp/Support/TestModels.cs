using System.Net;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Fictoshop.PlaywrightTests.Support;

public sealed record Credentials(string Username, string Password);

public sealed record ProductRecord(
    [property: JsonPropertyName("id")] int Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("description")] string Description,
    [property: JsonPropertyName("price")] decimal Price,
    [property: JsonPropertyName("in_stock")] int InStock);

public sealed record ReviewRecord(
    [property: JsonPropertyName("id")] int Id,
    [property: JsonPropertyName("user")] string User,
    [property: JsonPropertyName("rating")] decimal Rating,
    [property: JsonPropertyName("comment")] string Comment);

public sealed record OrderItemRecord(
    [property: JsonPropertyName("product_name")] string ProductName,
    [property: JsonPropertyName("unit_price")] decimal UnitPrice,
    [property: JsonPropertyName("quantity")] int Quantity,
    [property: JsonPropertyName("line_total")] decimal LineTotal);

public sealed record OrderRecord(
    [property: JsonPropertyName("id")] int Id,
    [property: JsonPropertyName("full_name")] string FullName,
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("phone")] string Phone,
    [property: JsonPropertyName("address")] string Address,
    [property: JsonPropertyName("postal_code")] string PostalCode,
    [property: JsonPropertyName("city")] string City,
    [property: JsonPropertyName("country")] string Country,
    [property: JsonPropertyName("total_amount")] decimal TotalAmount,
    [property: JsonPropertyName("items")] IReadOnlyList<OrderItemRecord> Items);

public sealed record DatabaseSnapshot(
    [property: JsonPropertyName("orders")] IReadOnlyList<int> Orders,
    [property: JsonPropertyName("reviews")] IReadOnlyList<int> Reviews,
    [property: JsonPropertyName("products")] IReadOnlyList<int> Products,
    [property: JsonPropertyName("users")] IReadOnlyList<int> Users);

public sealed record ApiResponse(HttpStatusCode Status, string Text, JsonElement Json)
{
    public bool IsSuccess => (int)Status is >= 200 and < 300;
}

public sealed class ScenarioState
{
    public Dictionary<string, ProductRecord> Products { get; } = new();
    public Dictionary<string, string> Shipping { get; set; } = new();
    public Credentials? Admin { get; set; }
    public Credentials? User { get; set; }
    public ReviewRecord? Review { get; set; }
    public OrderRecord? Order { get; set; }
    public ApiResponse? Response { get; set; }
    public string SelectedProductName { get; set; } = "";
    public string SearchQuery { get; set; } = "";
    public string ReviewComment { get; set; } = "";
    public string UpdatedReviewComment { get; set; } = "";
    public int Rating { get; set; } = 4;
    public int UpdatedRating { get; set; } = 5;
    public int InitialProductCount { get; set; }
    public int InitialOrderCount { get; set; }
    public int InitialStock { get; set; }
    public int InitialSecondaryStock { get; set; }
    public int? LastBrowserStatus { get; set; }
    public string LastBrowserBody { get; set; } = "";
    public List<string> RequestedUrls { get; } = new();
    public string ConfiguredIosBase { get; set; } = "";
    public List<OrderItemRecord> ExpectedItems { get; } = new();
}
