using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class AuthenticationPage
{
    private readonly IPage _page;
    private readonly ILocator _username;
    private readonly ILocator _password;
    private readonly ILocator _loginButton;

    public AuthenticationPage(IPage page)
    {
        _page = page;
        _username = page.GetByLabel("Username");
        _password = page.GetByLabel("Password");
        _loginButton = page.GetByRole(AriaRole.Button, new() { Name = "Log in" });
    }

    public async Task OpenFromStorefrontAsync()
    {
        await _page.GotoAsync(TestSettings.BaseUrl);
        await _page.Locator("header").GetByRole(AriaRole.Link, new() { Name = "Log in", Exact = true }).ClickAsync();
    }

    public Task OpenAsync() => _page.GotoAsync(TestSettings.BaseUrl + "/signin");
    public Task SubmitAsync() => _loginButton.ClickAsync();

    public async Task SubmitInvalidAsync()
    {
        await _username.FillAsync("unknown-playwright-user");
        await _password.FillAsync("Invalid-Playwright-Password!");
        await SubmitAsync();
    }

    public async Task LoginAsync(Credentials credentials)
    {
        await OpenAsync();
        await _username.FillAsync(credentials.Username);
        await _password.FillAsync(credentials.Password);
        await SubmitAsync();
        var destination = credentials.Username.Contains("_admin_", StringComparison.Ordinal)
            ? TestSettings.BaseUrl + "/admin/"
            : TestSettings.BaseUrl + "/";
        await _page.WaitForURLAsync(destination);
    }

    public async Task AssertCredentialFieldsAsync()
    {
        await Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/signin");
        await Expect(_username).ToBeVisibleAsync();
        await Expect(_password).ToBeVisibleAsync();
    }

    public Task AssertLoginButtonAsync() => Expect(_loginButton).ToBeVisibleAsync();

    public async Task AssertMissingCredentialsAsync()
    {
        Assert.That(await _username.EvaluateAsync<bool>("element => element.validity.valueMissing"), Is.True);
        Assert.That(await _username.EvaluateAsync<string>("element => element.validationMessage"), Is.Not.Empty);
    }

    public async Task AssertSignedOutAsync()
    {
        await _page.GotoAsync(TestSettings.BaseUrl);
        await Expect(_page.Locator("header").GetByRole(AriaRole.Link, new() { Name = "Log in", Exact = true })).ToBeVisibleAsync();
    }

    public Task AssertInvalidCredentialsAsync() => Expect(_page.GetByRole(AriaRole.Status)).ToHaveTextAsync("Invalid credentials");

    public async Task AssertSignInPageAsync()
    {
        await Expect(_page).ToHaveURLAsync(TestSettings.BaseUrl + "/signin");
        await Expect(_username).ToBeVisibleAsync();
        await Expect(_password).ToBeVisibleAsync();
    }
}
