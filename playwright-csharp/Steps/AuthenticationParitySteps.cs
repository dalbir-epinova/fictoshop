using Fictoshop.PlaywrightTests.Pages;
using Fictoshop.PlaywrightTests.Support;
using Microsoft.Playwright;
using NUnit.Framework;
using Reqnroll;

namespace Fictoshop.PlaywrightTests.Steps;

[Binding]
[Scope(Tag = "authentication")]
public sealed class AuthenticationParitySteps
{
    private readonly IPage _page;
    private readonly DjangoTestData _data;
    private readonly ScenarioState _state;
    private readonly AuthenticationPage _auth;
    private readonly CatalogPage _catalog;
    private readonly ReviewsPage _reviews;
    private readonly DjangoAdminPage _admin;

    public AuthenticationParitySteps(ScenarioContext context)
    {
        _page = context.Get<IPage>();
        _data = context.Get<DjangoTestData>();
        _state = context.Get<ScenarioState>();
        _auth = new AuthenticationPage(_page);
        _catalog = new CatalogPage(_page);
        _reviews = new ReviewsPage(_page);
        _admin = new DjangoAdminPage(_page);
        _state.ReviewComment = $"Playwright review {Guid.NewGuid():N}"[..26];
        _state.UpdatedReviewComment = $"Updated Playwright review {Guid.NewGuid():N}"[..34];
    }

    [Given("the customer is signed out")]
    public Task GivenSignedOut() => _page.Context.ClearCookiesAsync();

    [Given("the customer is on the sign-in page")]
    public async Task GivenOnSignIn()
    {
        await _page.Context.ClearCookiesAsync();
        await _auth.OpenAsync();
    }

    [When("the customer selects \"Log in\"")]
    public Task WhenSelectsLogin() => _auth.OpenFromStorefrontAsync();

    [Then("the sign-in page shows username and password fields")]
    public Task ThenCredentialFields() => _auth.AssertCredentialFieldsAsync();

    [Then("it shows a \"Log in\" button")]
    public Task ThenLoginButton() => _auth.AssertLoginButtonAsync();

    [When("the customer submits without both credentials")]
    public Task WhenSubmitsEmpty() => _auth.SubmitAsync();

    [Then("a message asks for username and password")]
    public Task ThenMissingMessage() => _auth.AssertMissingCredentialsAsync();

    [Then("the customer remains signed out")]
    public Task ThenRemainsSignedOut() => _auth.AssertSignedOutAsync();

    [When("the customer submits invalid credentials")]
    public Task WhenInvalidCredentials() => _auth.SubmitInvalidAsync();

    [Then("\"Invalid credentials\" is displayed")]
    public Task ThenInvalidDisplayed() => _auth.AssertInvalidCredentialsAsync();

    [Then("the customer remains on the sign-in page")]
    public Task ThenRemainsOnSignIn() => _auth.AssertSignInPageAsync();

    [Given("a regular user exists")]
    public async Task GivenRegularUser() => _state.User = await _data.CreateUserAsync(false);

    [When("the user signs in with valid credentials")]
    public Task WhenUserSignsIn() => _auth.LoginAsync(User);

    [Then("the storefront opens")]
    public Task ThenStorefrontOpens() => _catalog.AssertOpenAsync();

    [Then("the navigation identifies the signed-in user")]
    public Task ThenUserIdentified() => _catalog.AssertSignedInUserAsync(User.Username);

    [Then("a \"Log out\" button is visible")]
    public Task ThenLogoutVisible() => _catalog.AssertLogoutButtonAsync();

    [Given("a superuser exists")]
    public async Task GivenSuperuser() => _state.Admin = await _data.CreateUserAsync(true);

    [When("the superuser signs in with valid credentials")]
    public Task WhenSuperuserSignsIn() => _auth.LoginAsync(Admin);

    [Then("Django administration opens")]
    public Task ThenAdminOpens() => _admin.AssertIndexAsync();

    [When("the customer opens a product detail page")]
    public async Task WhenGuestOpensProduct()
    {
        await EnsureProductAsync();
        await _reviews.OpenAsync(Product.Id);
    }

    [Then("the review form is hidden")]
    public Task ThenReviewHidden() => _reviews.AssertFormHiddenAsync();

    [Then("a sign-in link for leaving a review is visible")]
    public Task ThenReviewSignIn() => _reviews.AssertSignInLinkAsync();

    [Given("a regular user is signed in")]
    public async Task GivenUserSignedIn()
    {
        await EnsureUserAsync();
        await _auth.LoginAsync(User);
        await _catalog.AssertOpenAsync();
    }

    [When("the user opens a product detail page")]
    public async Task WhenUserOpensProduct()
    {
        await EnsureProductAsync();
        await _reviews.OpenAsync(Product.Id);
    }

    [Then("the rating picker and feedback field are visible")]
    public Task ThenReviewFields() => _reviews.AssertFieldsAsync();

    [Then("the \"Submit review\" button is visible")]
    public Task ThenSubmitVisible() => _reviews.AssertSubmitAsync();

    [Given("a regular user is signed in on a product detail page")]
    public async Task GivenSignedInOnProduct()
    {
        await EnsureUserAsync();
        await EnsureProductAsync();
        await _auth.LoginAsync(User);
        await _catalog.AssertOpenAsync();
        await _reviews.OpenAsync(Product.Id);
    }

    [When("the user submits feedback without selecting a rating")]
    public Task WhenFeedbackWithoutRating() => _reviews.SubmitFeedbackWithoutRatingAsync("Feedback without a selected Playwright rating.");

    [Then("the review is not created")]
    public async Task ThenReviewNotCreated() => Assert.That(await _data.CountReviewsAsync(Product.Id, User.Username), Is.Zero);

    [Then("a message asks the user to select a rating")]
    public Task ThenRatingRequired() => _reviews.AssertRatingRequiredAsync();

    [When("the user selects a rating without entering feedback")]
    public Task WhenRatingWithoutFeedback() => _reviews.SelectRatingAsync(4);

    [When("submits the review")]
    public Task WhenSubmitsReview() => _reviews.SubmitAsync();

    [Then("a message asks the user to provide feedback")]
    public Task ThenFeedbackRequired() => _reviews.AssertFeedbackRequiredAsync();

    [When("the user selects a valid rating")]
    public Task WhenSelectsValidRating() => _reviews.SelectRatingAsync(_state.Rating);

    [When("enters feedback")]
    public Task WhenEntersFeedback() => _reviews.EnterFeedbackAsync(_state.ReviewComment);

    [Then("the review appears with username, rating, comment, and date")]
    public Task ThenReviewAppears() => _reviews.AssertReviewAsync(User.Username, _state.Rating, _state.ReviewComment);

    [Then("the product rating summary is updated")]
    public Task ThenSummaryUpdated() => _reviews.AssertRatingSummaryAsync(_state.Rating, 1);

    [Given("the signed-in user has already reviewed the product")]
    public async Task GivenExistingReview()
    {
        await EnsureUserAsync();
        await EnsureProductAsync();
        _state.Review = await _data.CreateReviewAsync(Product, User, 2m, "Original Playwright review.");
        await _auth.LoginAsync(User);
        await _reviews.OpenAsync(Product.Id);
    }

    [When("the user changes the rating and feedback")]
    public async Task WhenChangesReview()
    {
        await _reviews.SelectRatingAsync(_state.UpdatedRating);
        await _reviews.EnterFeedbackAsync(_state.UpdatedReviewComment);
    }

    [When("selects \"Update review\"")]
    public Task WhenUpdatesReview() => _reviews.SubmitUpdatedAsync();

    [Then("the existing review is updated")]
    public Task ThenExistingUpdated() => _reviews.AssertReviewAsync(User.Username, _state.UpdatedRating, _state.UpdatedReviewComment);

    [Then("no second review from that user is created")]
    public async Task ThenNoSecondReview() => Assert.That(await _data.CountReviewsAsync(Product.Id, User.Username), Is.EqualTo(1));

    private ProductRecord Product => _state.Products["review"];
    private Credentials User => _state.User ?? throw new InvalidOperationException("Regular user is missing.");
    private Credentials Admin => _state.Admin ?? throw new InvalidOperationException("Admin user is missing.");

    private async Task EnsureUserAsync() => _state.User ??= await _data.CreateUserAsync(false);

    private async Task EnsureProductAsync()
    {
        if (!_state.Products.ContainsKey("review"))
        {
            var reference = Guid.NewGuid().ToString("N")[..8];
            _state.Products["review"] = await _data.CreateProductAsync($"Playwright product {reference}", "Product created for Playwright authentication scenarios.", 49.95m, 7);
        }
    }
}
