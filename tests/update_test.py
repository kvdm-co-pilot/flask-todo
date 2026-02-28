# test_update_todo.py

from app import app
from flask import url_for, redirect
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestUpdateTodo:
    def test_valid_update(self, client):
        """
        Scenario: Update Todo Successfully
        Expected: Todo is updated and redirected to home page
        """
        # Given
        valid_todo_id = 1  # Assuming a todo with ID 1 exists
        new_data = {'title': 'Updated Title', 'description': 'Updated Description'}

        # When
        response = client.post(url_for('update', todo_id=valid_todo_id), data=new_data)

        # Then
        assert response.status_code == 302, "Expected a redirect after successful update"
        assert response.headers['Location'] == url_for('home'), "Should redirect to home page"

    def test_update_non_existent(self, client):
        """
        Scenario: Update Non-Existent Todo
        Expected: 404 error returned
        """
        # Given
        non_existent_todo_id = 9999  # Assuming this ID doesn't exist
        new_data = {'title': 'Title', 'description': 'Description'}

        # When
        response = client.post(url_for('update', todo_id=non_existent_todo_id), data=new_data)

        # Then
        assert response.status_code == 404, "Expected a 404 error for non-existent todo"

    def test_update_task_description(self, client):
        """
        Scenario: Update an existing task
        Expected: Task description updated successfully
        """
        # Given
        existing_todo_id = 2  # Assuming a todo with ID 2 exists
        new_data = {'description': 'Updated Task Description'}

        # When
        response = client.post(url_for('update', todo_id=existing_todo_id), data=new_data)

        # Then
        assert response.status_code == 302, "Expected a redirect after successful update"
        assert response.headers['Location'] == url_for('home'), "Should redirect to home page"
