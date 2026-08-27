using System.Net.Http.Json;
using System.Text.Json;

namespace Fictoshop.PlaywrightTests.Support;

public sealed class StorefrontApi : IDisposable
{
    private readonly HttpClient _client = new()
    {
        BaseAddress = new Uri(TestSettings.BaseUrl),
        Timeout = TimeSpan.FromSeconds(10),
    };

    public Task<ApiResponse> GetAsync(string path) => SendAsync(HttpMethod.Get, path);

    public Task<ApiResponse> DeleteAsync(string path) => SendAsync(HttpMethod.Delete, path);

    public Task<ApiResponse> PostAsync(string path, object body) => SendAsync(HttpMethod.Post, path, body);

    public void Dispose() => _client.Dispose();

    private async Task<ApiResponse> SendAsync(HttpMethod method, string path, object? body = null)
    {
        using var request = new HttpRequestMessage(method, path);
        request.Headers.Accept.ParseAdd("application/json");
        if (body is not null)
        {
            request.Content = new StringContent(JsonSerializer.Serialize(body, body.GetType()), System.Text.Encoding.UTF8, "application/json");
        }

        using var response = await _client.SendAsync(request);
        var text = await response.Content.ReadAsStringAsync();
        JsonElement json = default;
        if (!string.IsNullOrWhiteSpace(text))
        {
            using var document = JsonDocument.Parse(text);
            json = document.RootElement.Clone();
        }

        return new ApiResponse(response.StatusCode, text, json);
    }
}
