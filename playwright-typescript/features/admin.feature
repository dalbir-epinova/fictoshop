@admin @regression
Feature: Manage products and orders in Django administration
  As an administrator
  I want to manage catalog data and inspect orders
  So that the store can be operated

  Scenario: Guest cannot access administration
    Given the customer is signed out
    When the customer opens "/admin/"
    Then the Django admin login page is displayed

  @smoke
  Scenario: Superuser opens administration
    Given a superuser is signed in
    When the superuser opens "/admin/"
    Then the administration index is visible
    And Products and Orders are listed

  Scenario: Administrator creates a product
    Given a superuser is signed in
    When the superuser opens the new product form
    And enters a valid product name, description, price, and stock
    And uploads a dummy product image
    And saves the product
    Then the product appears in Django administration
    And the product appears in the storefront catalog
    And the product image is displayed in the storefront catalog

  Scenario: Administrator updates product stock
    Given a superuser is signed in
    And a product exists
    When the superuser changes its stock value
    Then the new stock value appears in the storefront

  Scenario: Administrator views an order and its lines
    Given a customer order exists
    And a superuser is signed in
    When the superuser opens that order in administration
    Then customer, shipping, total, and creation details are visible
    And each order line is visible as read-only data
