@checkout @regression
Feature: Place and confirm an order
  As a customer with products in my cart
  I want to provide shipping details and place an order
  So that my purchase is recorded and can be delivered

  Background:
    Given the cart has been cleared
    And an available product exists

  Scenario: Empty cart cannot enter checkout
    When the customer opens "/checkout" with an empty cart
    Then the customer is redirected to the storefront

  @smoke
  Scenario: Checkout displays shipping form and order summary
    Given the customer has added a product to the cart
    When the customer selects "Checkout"
    Then the shipping details page opens
    And fields for name, email, phone, address, postal code, city, and country are visible
    And the ordered product, quantity, and total are visible

  Scenario: Customer returns from checkout to cart
    Given the customer is on checkout with a product in the cart
    When the customer selects "Back to cart"
    Then the storefront opens at the cart
    And the product remains in the cart

  @negative
  Scenario Outline: Required shipping detail is missing
    Given the customer is on checkout with a product in the cart
    When the customer submits valid shipping details except for "<field>"
    Then the order is not placed
    And a validation message is shown for "<field>"

    Examples:
      | field       |
      | Full name   |
      | Email       |
      | Phone       |
      | Address     |
      | Postal code |
      | City        |
      | Country     |

  @negative
  Scenario: Invalid email is rejected
    Given the customer is on checkout with a product in the cart
    When the customer enters an invalid email address
    And attempts to place the order
    Then the order is not placed
    And the email field reports a validation error

  @smoke
  Scenario: Customer places an order successfully
    Given the customer is on checkout with a product in the cart
    When the customer enters valid shipping details
    And selects "Place order"
    Then an order confirmation page opens
    And a unique order number is displayed
    And the page confirms that the order was placed successfully

  Scenario: Confirmation summarizes ordered items
    When the customer places a valid order containing multiple products
    Then every product name, unit price, quantity, and line total is shown
    And the correct order total is shown

  Scenario: Confirmation summarizes shipping details
    When the customer places an order with valid shipping details
    Then the confirmation shows the customer's name
    And it shows the address, postal code, city, and country
    And it shows the email and phone number

  Scenario: Successful order updates storefront state
    When the customer places a valid order
    And returns to the storefront
    Then the floating cart is hidden
    And product stock is reduced by the purchased quantity

  Scenario: Back to storefront returns to catalog
    Given the customer has placed an order
    When the customer selects "Back to storefront"
    Then the storefront heading and catalog are visible

  @security
  Scenario: Another browser session cannot view the confirmation
    Given a customer has placed an order in one browser session
    When a different browser session opens that confirmation URL
    Then a 404 response is returned
    And no customer or shipping details are exposed

  @negative
  Scenario: Stock changes before order placement
    Given the customer has products in the cart
    And one product no longer has enough stock
    When the customer submits valid shipping details
    Then no order is created
    And an insufficient-stock message identifies the product
    And no product stock is reduced
    And the cart remains unchanged

