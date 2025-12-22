# test_add_todo.py

# Imports
import pytest
from flask import Flask, request
from myapp.app import app

# Unique Test Class
class TestAddToDoItem:

    @pytest.fixture(scope='function')
    def test_client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_todo_list(self):
        # This is a mock list for testing purposes
        return []

    def test_add_valid_todo_item(self, test_client, sample_todo_list):
        # Given: A valid title
        title = 'Buy Groceries'

        # When: Adding a new to-do item
        response = test_client.post('/add', data={'title': title})

        # Then: Assert the item is added
        assert response.status_code == 200  # Assuming 200 is success
        sample_todo_list.append(title)
        assert 'Buy Groceries' in sample_todo_list

    def test_add_empty_todo_item(self, test_client, sample_todo_list):
        # Given: An empty title
        title = ''

        # When: Attempting to add the item
        response = test_client.post('/add', data={'title': title})

        # Then: Assert an error message appears
        assert response.status_code == 400  # Assuming 400 is for bad request
        assert title not in sample_todo_list

    def test_add_max_length_todo_item(self, test_client, sample_todo_list):
        # Given: A maximum length title
        title = 'a' * 100

        # When: Adding the item
        response = test_client.post('/add', data={'title': title})

        # Then: Assert the item is added
        assert response.status_code == 200  # Assuming 200 is success
        sample_todo_list.append(title)
        assert title in sample_todo_list

    def test_add_exceeding_length_todo_item(self, test_client, sample_todo_list):
        # Given: An exceeding length title
        title = 'a' * 101

        # When: Adding the item
        response = test_client.post('/add', data={'title': title})

        # Then: Assert an error message appears
        assert response.status_code == 400  # Assuming 400 is for bad request
        assert title not in sample_todo_list

    def test_add_special_character_todo_item(self, test_client, sample_todo_list):
        # Given: A title with special characters
        title = '!@#$%^&*()'

        # When: Adding the item
        response = test_client.post('/add', data={'title': title})

        # Then: Assert the item is added
        assert response.status_code == 200  # Assuming 200 is success
        sample_todo_list.append(title)
        assert title in sample_todo_list

    def test_server_error_on_add(self, test_client, sample_todo_list):
        # Hypothetical test for server error
        # Given: A server error scenario
        title = 'Server Test'

        # When: Adding the item during downtime
        # This is a hypothetical scenario
        # response = test_client.post('/add', data={'title': title})

        # Then: Assert an error message appears
        # assert response.status_code == 500  # Assuming 500 is for server error
        # assert title not in sample_todo_list

# Test Execution
if __name__ == "__main__":
    pytest.main()
