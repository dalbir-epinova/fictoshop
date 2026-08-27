using System.Text.RegularExpressions;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using static Microsoft.Playwright.Assertions;

namespace Fictoshop.PlaywrightTests.Pages;

public sealed class ReviewsPage
{
    private readonly IPage _page;

    public ReviewsPage(IPage page)
    {
        _page = page;
    }

    public Task OpenAsync(int productId) => _page.GotoAsync($"{TestSettings.BaseUrl}/products/{productId}/view");
    public Task AssertFormHiddenAsync() => Expect(_page.Locator("form.review-form")).ToHaveCountAsync(0);

    public async Task AssertSignInLinkAsync()
    {
        var link = _page.Locator("#reviews").GetByRole(AriaRole.Link, new() { Name = "Sign in", Exact = true });
        await Expect(link).ToBeVisibleAsync();
        await Expect(link).ToHaveAttributeAsync("href", "/signin?next=" + _page.Url.Replace(TestSettings.BaseUrl, ""));
    }

    public async Task AssertFieldsAsync()
    {
        await Expect(_page.GetByRole(AriaRole.Radiogroup, new() { Name = "Select a rating" })).ToBeVisibleAsync();
        await Expect(_page.GetByLabel("Feedback")).ToBeVisibleAsync();
    }

    public Task AssertSubmitAsync() => Expect(_page.GetByRole(AriaRole.Button, new() { Name = "Submit review", Exact = true })).ToBeVisibleAsync();

    public async Task SubmitFeedbackWithoutRatingAsync(string feedback)
    {
        await _page.GetByLabel("Feedback").FillAsync(feedback);
        await SubmitAsync();
    }

    public Task AssertRatingRequiredAsync() => Expect(_page.Locator(".form-error")).ToHaveTextAsync("Select a rating using the stars.");

    public async Task SelectRatingAsync(int rating)
    {
        var button = _page.Locator($".star-picker-button[data-index=\"{rating}\"]");
        var box = await button.BoundingBoxAsync();
        Assert.That(box, Is.Not.Null);
        await button.ClickAsync(new LocatorClickOptions { Position = new Position { X = box!.Width * .75f, Y = box.Height / 2 } });
        await Expect(_page.Locator("#review-rating-value")).ToHaveValueAsync($"{rating:F1}");
    }

    public Task SubmitAsync() => _page.GetByRole(AriaRole.Button, new() { Name = "Submit review", Exact = true }).ClickAsync();
    public Task SubmitUpdatedAsync() => _page.GetByRole(AriaRole.Button, new() { Name = "Update review", Exact = true }).ClickAsync();

    public async Task AssertFeedbackRequiredAsync()
    {
        var field = _page.GetByLabel("Feedback");
        Assert.That(await field.EvaluateAsync<bool>("element => element.validity.valueMissing"), Is.True);
        Assert.That(await field.EvaluateAsync<string>("element => element.validationMessage"), Is.Not.Empty);
    }

    public Task EnterFeedbackAsync(string feedback) => _page.GetByLabel("Feedback").FillAsync(feedback);

    public async Task AssertReviewAsync(string username, int rating, string comment)
    {
        var review = _page.Locator(".review-list li").Filter(new() { HasText = username });
        await Expect(review).ToHaveCountAsync(1);
        await Expect(review).ToContainTextAsync(comment);
        await Expect(review.Locator(".review-rating")).ToHaveAttributeAsync("data-rating", $"{rating:F1}");
        await Expect(review.Locator(".review-header span")).ToHaveTextAsync(new Regex(@"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}$"));
    }

    public async Task AssertRatingSummaryAsync(int rating, int count)
    {
        var summary = _page.Locator(".product-detail-rating");
        await Expect(summary).ToContainTextAsync($"{rating:F1} / 5");
        await Expect(summary).ToContainTextAsync($"({count} reviews)");
    }
}
