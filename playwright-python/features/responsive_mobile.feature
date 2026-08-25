@responsive @mobile @regression
Feature: Use Fictoshop on smaller screens and app WebViews
  As a mobile customer
  I want the storefront and checkout to fit my screen
  So that I can complete an order without obstructed controls

  Scenario Outline: Storefront works at a supported mobile viewport
    Given the browser viewport is "<viewport>"
    When the customer opens the storefront
    Then the heading and catalog fit within the viewport
    And primary controls are usable without horizontal scrolling

    Examples:
      | viewport    |
      | 390 x 844   |
      | 412 x 915   |
      | 768 x 1024  |

  Scenario: Mobile floating cart fits inside viewport
    Given the browser uses a mobile viewport
    When the customer adds a product to the cart
    Then the entire floating cart width remains inside the viewport
    And the cart lines can scroll when their content exceeds the maximum height
    And "Clear" and "Checkout" remain usable

  Scenario: Mobile checkout form uses a single column
    Given the browser uses a mobile viewport
    And the cart contains a product
    When the customer opens checkout
    Then shipping fields are arranged in one column
    And "Back to cart" and "Place order" are usable

  @android
  Scenario: Android bundle calls the host development server
    Given the storefront is running in an Android emulator
    When the mobile bundle requests products
    Then it uses "http://10.0.2.2:8000"
    And catalog products are displayed

  @ios
  Scenario: iOS bundle uses configured API base
    Given the storefront is running in the iOS app
    When the mobile bundle requests products
    Then it uses the configured "API_BASE_URL"
    And catalog products are displayed
