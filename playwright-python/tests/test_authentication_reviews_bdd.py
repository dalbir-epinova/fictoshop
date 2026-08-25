from pytest_bdd import scenario


@scenario(
    "../features/authentication_reviews.feature",
    "Guest opens sign-in page",
)
def test_guest_opens_sign_in_page():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Missing login credentials are rejected in the browser",
)
def test_missing_login_credentials_are_rejected_in_the_browser():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Invalid credentials are rejected",
)
def test_invalid_credentials_are_rejected():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Regular user signs in",
)
def test_regular_user_signs_in():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Administrator signs in",
)
def test_administrator_signs_in():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Guest is prompted to sign in before reviewing",
)
def test_guest_is_prompted_to_sign_in_before_reviewing():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Signed-in user sees the review form",
)
def test_signed_in_user_sees_the_review_form():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Review without rating is rejected",
)
def test_review_without_rating_is_rejected():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "Review without feedback is rejected",
)
def test_review_without_feedback_is_rejected():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "User submits a product review",
)
def test_user_submits_a_product_review():
    pass


@scenario(
    "../features/authentication_reviews.feature",
    "User updates an existing review",
)
def test_user_updates_an_existing_review():
    pass
