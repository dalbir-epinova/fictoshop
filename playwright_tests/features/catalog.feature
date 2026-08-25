Feature: Browse catalog and manage cart
  As a visitor
  I want to browse the storefront and add items to my cart
  So that I can verify the shop is functional end-to-end

  Scenario: Guest adds a product to the cart from the catalog
    Given the storefront service is up
    When I open the storefront home page
    Then I can see the hero content
    And I can see products listed
    When I add the first listed product to the cart
    Then the cart summary shows at least one item

  Scenario: Guest goes to login
    Given I open the storefront home page
    When I click on "Log in" button
    Then The "sign_in" page is shown