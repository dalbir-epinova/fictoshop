@authentication @reviews @regression
Feature: Sign in and review products
  As a customer
  I want to authenticate and leave product feedback
  So that other customers can learn from my experience

  @smoke
  Scenario: Guest opens sign-in page
    Given the customer is signed out
    When the customer selects "Log in"
    Then the sign-in page shows username and password fields
    And it shows a "Log in" button

  @negative
  Scenario: Missing login credentials are rejected in the browser
    Given the customer is on the sign-in page
    When the customer submits without both credentials
    Then a message asks for username and password
    And the customer remains signed out

  @negative
  Scenario: Invalid credentials are rejected
    Given the customer is on the sign-in page
    When the customer submits invalid credentials
    Then "Invalid credentials" is displayed
    And the customer remains on the sign-in page

  Scenario: Regular user signs in
    Given a regular user exists
    When the user signs in with valid credentials
    Then the storefront opens
    And the navigation identifies the signed-in user
    And a "Log out" button is visible

  Scenario: Administrator signs in
    Given a superuser exists
    When the superuser signs in with valid credentials
    Then Django administration opens

  Scenario: Signed-in user logs out
    Given a regular user is signed in
    When the user selects "Log out"
    Then the storefront opens
    And the navigation shows "Log in"

  Scenario: Guest is prompted to sign in before reviewing
    Given the customer is signed out
    When the customer opens a product detail page
    Then the review form is hidden
    And a sign-in link for leaving a review is visible

  Scenario: Signed-in user sees the review form
    Given a regular user is signed in
    When the user opens a product detail page
    Then the rating picker and feedback field are visible
    And the "Submit review" button is visible

  @negative
  Scenario: Review without rating is rejected
    Given a regular user is signed in on a product detail page
    When the user submits feedback without selecting a rating
    Then the review is not created
    And a message asks the user to select a rating

  @negative
  Scenario: Review without feedback is rejected
    Given a regular user is signed in on a product detail page
    When the user selects a rating without entering feedback
    And submits the review
    Then the review is not created
    And a message asks the user to provide feedback

  @smoke
  Scenario: User submits a product review
    Given a regular user is signed in on a product detail page
    When the user selects a valid rating
    And enters feedback
    And submits the review
    Then the review appears with username, rating, comment, and date
    And the product rating summary is updated

  Scenario: User updates an existing review
    Given the signed-in user has already reviewed the product
    When the user changes the rating and feedback
    And selects "Update review"
    Then the existing review is updated
    And no second review from that user is created

