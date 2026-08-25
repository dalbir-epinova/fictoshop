@cart @regression
Feature: Manage the floating shopping cart
  As a customer
  I want my cart to remain available while shopping
  So that I can review and change my intended purchase

  Background:
    Given the cart has been cleared
    And the catalog contains an available product
    And the customer opens the storefront

  @smoke
  Scenario: Empty cart is hidden
    Then the floating cart is not visible

  @smoke
  Scenario: Adding a product displays the floating cart
    When the customer adds 1 available product to the cart
    Then the floating cart is visible
    And it shows the product name
    And it shows 1 total item
    And it shows the correct total price

  Scenario: Floating cart remains visible while scrolling
    Given the customer has added a product to the cart
    When the customer scrolls to another part of the storefront
    Then the floating cart remains inside the viewport

  Scenario: Add a selected quantity
    When the customer selects quantity 3
    And adds the product to the cart
    Then the cart line shows quantity 3
    And the total equals three times the unit price

  Scenario: Adding the same product accumulates quantity
    Given the customer has added 1 product to the cart
    When the customer adds 2 more of the same product
    Then the cart contains one line for that product
    And the line quantity is 3

  Scenario: Cart calculates totals for multiple products
    When the customer adds multiple different products
    Then every selected product is shown in the cart
    And total items equal the sum of all quantities
    And the grand total equals the sum of all line totals

  Scenario: Remove one cart line
    Given the cart contains two different products
    When the customer removes one product
    Then only that product disappears from the cart
    And the totals are recalculated

  Scenario: Clear the entire cart
    Given the cart contains products
    When the customer selects "Clear"
    Then all cart lines are removed
    And the floating cart is hidden

  Scenario: Cart survives a page reload
    Given the customer has added a product to the cart
    When the customer reloads the storefront
    Then the same product and quantity remain in the cart

  @negative
  Scenario: Customer cannot add more than available stock
    When the customer attempts to add more units than available
    Then the request is rejected
    And a stock error is displayed
    And the cart quantity is unchanged

  Scenario: Removing an item restores its available catalog stock
    Given the customer has added a product to the cart
    When the customer removes that product from the cart
    Then the catalog shows the original available stock

