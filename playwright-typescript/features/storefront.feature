@storefront @regression
Feature: Browse the storefront catalog
  As a customer
  I want to find and inspect products
  So that I can decide what to buy

  Background:
    Given the catalog contains available and unavailable products
    And the customer opens the storefront

  @smoke
  Scenario: Storefront loads successfully
    Then the heading "Welcome to FictoShop" is visible
    And the catalog is visible
    And at least one product card is displayed

  Scenario: Product card shows purchasing information
    Then each product card shows its name
    And each product card shows its price
    And each product card shows its stock status
    And an available product has an enabled "Add to cart" button

  Scenario: Customer opens a product detail page
    When the customer selects a product name
    Then the product detail page opens
    And the product name, description, price, rating summary, and reviews section are visible

  Scenario: Search matches a product name
    When the customer searches for part of a product name
    Then only matching products are displayed
    And the catalog status shows the number of matches

  Scenario: Search matches a product description
    When the customer searches for text found only in a product description
    Then the matching product is displayed

  Scenario: Search has no matches
    When the customer searches for text that is not in the catalog
    Then no product cards are displayed
    And the empty search message is visible

  Scenario: Clearing search restores the catalog
    Given the customer has filtered the catalog using search
    When the customer clears the search field
    Then all products are displayed again

  Scenario: Sort products by lowest price
    When the customer selects "Price: Low to high"
    Then product prices are ordered from lowest to highest

  Scenario: Sort products by highest price
    When the customer selects "Price: High to low"
    Then product prices are ordered from highest to lowest

  Scenario: Sort products by stock level
    When the customer selects "Stock level"
    Then products are ordered from highest to lowest available stock

  Scenario: Show only products in stock
    When the customer enables "In stock only"
    Then products with zero available stock are hidden

  Scenario: Out-of-stock product cannot be added
    Then an out-of-stock product shows "Out of stock"
    And its quantity controls are disabled
    And its "Add to cart" button is disabled

  Scenario: Quantity controls stay within valid limits
    When the customer decreases the initial quantity
    Then the quantity remains 1
    When the customer increases the quantity beyond available stock
    Then the quantity does not exceed available stock

  @api_navigation
  Scenario: Explore API opens the product API
    When the customer selects "Explore the API"
    Then the browser opens the "/products" endpoint
    And the response contains catalog products
