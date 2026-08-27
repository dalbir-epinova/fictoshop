namespace Fictoshop.PlaywrightTests.Support;

public static class TestSettings
{
    public static string BaseUrl =>
        (Environment.GetEnvironmentVariable("FICTOSHOP_BASE_URL")
         ?? "http://127.0.0.1:8000")
        .TrimEnd('/');

    public static bool Headed => true;
}