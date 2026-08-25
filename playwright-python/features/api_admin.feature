@api @regression
Feature: Use the public storefront API
  As an API consumer
  I want predictable product and cart endpoints
  So that clients can use the storefront backend

  Scenario: API metadata lists available entry points
    When the client requests "/meta"
    Then the response is successful
    And it identifies the frontend, products, cart, login, and API exploration paths

  Scenario: Product collection returns products
    When the client requests "/products"
    Then the response is successful
    And each product contains id, name, description, price, stock, image, rating, and review count

  Scenario: Product detail returns one product and reviews
    Given a product with reviews exists
    When the client requests that product from "/products/<id>"
    Then the response contains the selected product
    And it contains the product reviews

  @negative
  Scenario: Unknown product returns not found
    When the client requests an unknown product id
    Then the API returns status 404
    And the response says "Product not found"

  Scenario: Add product through cart API
    Given an available product exists
    When the client posts its id and a valid quantity to "/cart"
    Then the API returns status 201
    And the response contains the updated items, item count, and total

  @negative
  Scenario Outline: Cart API rejects invalid input
    When the client posts product id "<product_id>" and quantity "<quantity>" to "/cart"
    Then the API returns status "<status>"

    Examples:
      | product_id | quantity | status |
      | 0          | 1        | 400    |
      | valid      | 0        | 400    |
      | unknown    | 1        | 404    |
      | valid      | too many | 400    |

  Scenario: Remove product through cart API
    Given the cart API contains a product
    When the client deletes "/cart/<product_id>"
    Then that product is absent from the returned cart

  Scenario: Clear cart through API
    Given the cart API contains products
    When the client deletes "/cart"
    Then the returned cart is empty
    And total items and grand total are zero

