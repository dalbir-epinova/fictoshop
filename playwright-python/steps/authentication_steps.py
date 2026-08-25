from decimal import Decimal

from decimal import Decimal

from pytest_bdd import given, then, when

from pages.sign_in_page import SignInPage
from pages.storefront_page import StorefrontPage
from pages.admin_page import AdminPage
from pages.product_detail_page import ProductDetailPage


@given("the customer is signed out")
def customer_is_signed_out(signed_out_context: object) -> None:
    # Depending on the fixture clears cookies before the browser steps run.
    assert signed_out_context is not None


@given("the customer is on the sign-in page")
def customer_is_on_sign_in_page(
    signed_out_context: object,
    sign_in_page: SignInPage,
) -> None:
    assert signed_out_context is not None
    sign_in_page.open()


@when('the customer selects "Log in"')
def customer_selects_log_in(sign_in_page: SignInPage) -> None:
    sign_in_page.open_from_storefront()


@then("the sign-in page shows username and password fields")
def sign_in_page_shows_credentials_fields(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_credentials_fields()


@then('it shows a "Log in" button')
def sign_in_page_shows_login_button(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_login_button()


@when("the customer submits without both credentials")
def customer_submits_without_credentials(sign_in_page: SignInPage) -> None:
    sign_in_page.submit()


@then("a message asks for username and password")
def message_asks_for_credentials(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_missing_credentials_message()


@then("the customer remains signed out")
def customer_remains_signed_out(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_customer_signed_out()


@when("the customer submits invalid credentials")
def customer_submits_invalid_credentials(sign_in_page: SignInPage) -> None:
    sign_in_page.submit_invalid_credentials()


@then('"Invalid credentials" is displayed')
def invalid_credentials_is_displayed(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_invalid_credentials_message()


@then("the customer remains on the sign-in page")
def customer_remains_on_sign_in_page(sign_in_page: SignInPage) -> None:
    sign_in_page.expect_sign_in_page()


@given("a regular user exists")
def regular_user_exists(regular_user_credentials: dict[str, str]) -> None:
    assert regular_user_credentials["username"]
    assert regular_user_credentials["password"]


@when("the user signs in with valid credentials")
def user_signs_in_with_valid_credentials(
    sign_in_page: SignInPage,
    regular_user_credentials: dict[str, str],
) -> None:
    sign_in_page.login(
        regular_user_credentials["username"],
        regular_user_credentials["password"],
    )


@then("the storefront opens")
def storefront_opens(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_open()


@then("the navigation identifies the signed-in user")
def navigation_identifies_signed_in_user(
    storefront_page: StorefrontPage,
    regular_user_credentials: dict[str, str],
) -> None:
    storefront_page.expect_signed_in_user(regular_user_credentials["username"])


@then('a "Log out" button is visible')
def logout_button_is_visible(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_logout_button()


@given("a superuser exists")
def superuser_exists(admin_credentials: dict[str, str]) -> None:
    assert admin_credentials["username"]
    assert admin_credentials["password"]


@when("the superuser signs in with valid credentials")
def superuser_signs_in_with_valid_credentials(
    sign_in_page: SignInPage,
    admin_credentials: dict[str, str],
) -> None:
    sign_in_page.login(
        admin_credentials["username"],
        admin_credentials["password"],
    )


@then("Django administration opens")
def django_administration_opens(admin_page: AdminPage) -> None:
    admin_page.expect_admin_index()


@when("the customer opens a product detail page")
def customer_opens_product_detail_page(
    product_detail_page: ProductDetailPage,
    existing_product: object,
) -> None:
    product_detail_page.open(existing_product.id)


@then("the review form is hidden")
def review_form_is_hidden(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_review_form_hidden()


@then("a sign-in link for leaving a review is visible")
def review_sign_in_link_is_visible(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_review_sign_in_link()


@given("a regular user is signed in")
def regular_user_is_signed_in(
    sign_in_page: SignInPage,
    storefront_page: StorefrontPage,
    regular_user_credentials: dict[str, str],
) -> None:
    sign_in_page.login(regular_user_credentials["username"], regular_user_credentials["password"])
    storefront_page.expect_open()


@when("the user opens a product detail page")
def user_opens_product_detail_page(product_detail_page: ProductDetailPage, existing_product: object) -> None:
    product_detail_page.open(existing_product.id)


@then("the rating picker and feedback field are visible")
def rating_picker_and_feedback_are_visible(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_rating_and_feedback_fields()


@then('the "Submit review" button is visible')
def submit_review_button_is_visible(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_submit_review_button()


@given("a regular user is signed in on a product detail page")
def regular_user_is_signed_in_on_product_detail_page(
    sign_in_page: SignInPage, storefront_page: StorefrontPage,
    product_detail_page: ProductDetailPage, regular_user_credentials: dict[str, str],
    existing_product: object,
) -> None:
    sign_in_page.login(regular_user_credentials["username"], regular_user_credentials["password"])
    storefront_page.expect_open()
    product_detail_page.open(existing_product.id)


@when("the user submits feedback without selecting a rating", target_fixture="submitted_review_comment")
def user_submits_feedback_without_rating(product_detail_page: ProductDetailPage) -> str:
    feedback = "Feedback without a selected Playwright rating."
    product_detail_page.submit_feedback_without_rating(feedback)
    return feedback


@then("the review is not created")
def review_is_not_created(existing_product: object, regular_user_credentials: dict[str, str]) -> None:
    from django.contrib.auth import get_user_model
    from shop.models import Review
    user = get_user_model().objects.get(username=regular_user_credentials["username"])
    assert not Review.objects.filter(product=existing_product, user=user).exists()


@then("a message asks the user to select a rating")
def message_asks_user_to_select_rating(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_rating_required_message()


@when("the user selects a rating without entering feedback")
def user_selects_rating_without_feedback(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.select_rating(4)


@when("submits the review")
def user_submits_review(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.submit_review()


@then("a message asks the user to provide feedback")
def message_asks_user_to_provide_feedback(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_feedback_required_message()


@when("the user selects a valid rating")
def user_selects_valid_rating(product_detail_page: ProductDetailPage, review_data: dict[str, object]) -> None:
    product_detail_page.select_rating(int(review_data["rating"]))


@when("enters feedback")
def user_enters_feedback(product_detail_page: ProductDetailPage, review_data: dict[str, object]) -> None:
    product_detail_page.enter_feedback(str(review_data["comment"]))


@then("the review appears with username, rating, comment, and date")
def review_appears_with_expected_details(product_detail_page: ProductDetailPage, regular_user_credentials: dict[str, str], review_data: dict[str, object]) -> None:
    product_detail_page.expect_review(regular_user_credentials["username"], int(review_data["rating"]), str(review_data["comment"]))


@then("the product rating summary is updated")
def product_rating_summary_is_updated(product_detail_page: ProductDetailPage, review_data: dict[str, object]) -> None:
    product_detail_page.expect_rating_summary(int(review_data["rating"]), 1)


@given("the signed-in user has already reviewed the product")
def signed_in_user_has_reviewed_product(sign_in_page: SignInPage, storefront_page: StorefrontPage, product_detail_page: ProductDetailPage, regular_user_credentials: dict[str, str], existing_user_review: object) -> None:
    sign_in_page.login(regular_user_credentials["username"], regular_user_credentials["password"])
    storefront_page.expect_open()
    product_detail_page.open(existing_user_review.product_id)


@when("the user changes the rating and feedback")
def user_changes_rating_and_feedback(product_detail_page: ProductDetailPage, review_data: dict[str, object]) -> None:
    product_detail_page.select_rating(int(review_data["updated_rating"]))
    product_detail_page.enter_feedback(str(review_data["updated_comment"]))


@when('selects "Update review"')
def user_selects_update_review(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.submit_updated_review()


@then("the existing review is updated")
def existing_review_is_updated(product_detail_page: ProductDetailPage, existing_user_review: object, regular_user_credentials: dict[str, str], review_data: dict[str, object]) -> None:
    existing_user_review.refresh_from_db()
    rating = int(review_data["updated_rating"]); comment = str(review_data["updated_comment"])
    assert existing_user_review.rating == Decimal(f"{rating}.0")
    assert existing_user_review.comment == comment
    product_detail_page.expect_review(regular_user_credentials["username"], rating, comment)


@then("no second review from that user is created")
def no_second_review_is_created(existing_user_review: object) -> None:
    from shop.models import Review
    assert Review.objects.filter(product_id=existing_user_review.product_id, user_id=existing_user_review.user_id).count() == 1
