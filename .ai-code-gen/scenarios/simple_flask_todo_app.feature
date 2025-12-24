Feature: Simple Flask Todo App
  Manage todo items using SQLAlchemy and SQLite database.

  @EXPECTED @confidence-medium
  Scenario: Add a new todo item with valid content
    Given the todo app is running
    When user adds a new todo item with content 'Buy groceries'
    Then the todo item should be added successfully
    # Source: Testable Behaviors Found: Adding a new todo item

  @EXPECTED @confidence-medium
  Scenario: Add a new todo item with empty content
    Given the todo app is running
    When user attempts to add a new todo item with empty content
    Then an error message should be displayed indicating content is required
    # Source: Edge Cases to Cover: Adding a todo item with empty content

  @EXPECTED @confidence-medium
  Scenario: Retrieve all todo items when none exist
    Given the todo app is running
    When user retrieves all todo items
    Then an empty list should be returned
    # Source: Edge Cases to Cover: Retrieving todo items when none exist

  @EXPECTED @confidence-medium
  Scenario: Update an existing todo item
    Given the todo app is running
    And a todo item with content 'Buy groceries' exists
    When user updates the todo item to 'Buy milk'
    Then the todo item should be updated successfully
    # Source: Testable Behaviors Found: Updating an existing todo item

  @EXPECTED @confidence-medium
  Scenario: Update a non-existent todo item
    Given the todo app is running
    When user attempts to update a non-existent todo item
    Then an error message should be displayed indicating the item does not exist
    # Source: Edge Cases to Cover: Updating a non-existent todo item

  @EXPECTED @confidence-medium
  Scenario: Delete an existing todo item
    Given the todo app is running
    And a todo item with content 'Buy groceries' exists
    When user deletes the todo item
    Then the todo item should be deleted successfully
    # Source: Testable Behaviors Found: Deleting a todo item

  @EXPECTED @confidence-medium
  Scenario: Delete a non-existent todo item
    Given the todo app is running
    When user attempts to delete a non-existent todo item
    Then an error message should be displayed indicating the item does not exist
    # Source: Edge Cases to Cover: Deleting a non-existent todo item

  @EXPECTED @confidence-medium
  Scenario: Test for SQL injection vulnerability
    Given the todo app is running
    When user attempts to add a todo item with content '1; DROP TABLE todos;'
    Then the application should prevent SQL injection and display an error message
    # Source: Focus Areas: Test for SQL injection vulnerabilities
