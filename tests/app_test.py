# test_app.py

# Correct package declaration

# Imports
import pytest
from flask import url_for
from app import app, db, Todo  # Adjust the path according to your project structure


# Sample Test Case Class

class TestApp:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """
        Set up and teardown fixture to initialize the app context and
        clear the database after each test.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield  # This is where the testing happens
            db.session.remove()
            db.drop_all()

    def test_add_new_todo_item_valid_title(self, client):
        """
        [EXACT] Functional_AddNewTodoItem_ValidTitle
        Scenario: Add a new todo item
        Test adding a valid todo item title to the list.
        """
        # Given
        title = 'Buy groceries'
        # When
        response = client.post(url_for('add'), data={'title': title})
        # Then
        assert response.status_code == 302  # Redirect indicates success
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == title
        assert not todos[0].complete  # Incomplete by default

    def test_update_todo_item_status_valid_id(self, client):
        """
        [EXACT] Functional_UpdateTodoItemStatus_ValidId
        Scenario: Update the status of a todo item
        Test updating the status of an existing todo item.
        """
        # Given
        todo = Todo(title='Test Item', complete=False)
        db.session.add(todo)
        db.session.commit()
        # When
        response = client.get(url_for('update', todo_id=todo.id))
        # Then
        assert response.status_code == 302  # Redirect indicates success
        updated_todo = Todo.query.get(todo.id)
        assert updated_todo.complete  # Status should be toggled

    def test_delete_todo_item_valid_id(self, client):
        """
        [EXACT] Functional_DeleteTodoItem_ValidId
        Scenario: Delete a todo item
        Test deleting an existing todo item from the list.
        """
        # Given
        todo = Todo(title='Test Item', complete=False)
        db.session.add(todo)
        db.session.commit()
        # When
        response = client.get(url_for('delete', todo_id=todo.id))
        # Then
        assert response.status_code == 302  # Redirect indicates success
        deleted_todo = Todo.query.get(todo.id)
        assert deleted_todo is None  # Todo should be deleted

    def test_add_todo_item_max_title_length(self, client):
        """
        [BOUNDARY] Functional_AddTodoItem_MaxTitleLength
        Scenario: Add a todo item with maximum title length
        Test adding a todo item with the maximum allowed title length.
        """
        # Given
        title = 'x' * 100  # Max length
        # When
        response = client.post(url_for('add'), data={'title': title})
        # Then
        assert response.status_code == 302  # Redirect indicates success
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == title

    def test_add_todo_item_empty_title(self, client):
        """
        [NEGATIVE] Functional_AddTodoItem_EmptyTitle
        Scenario: Add a todo item with an empty title
        Test adding a todo item with an empty title.
        """
        # When
        response = client.post(url_for('add'), data={'title': ''})
        # Then
        assert response.status_code != 302  # Should not redirect, indicating failure


# Test Execution
if __name__ == "__main__":
    pytest.main()