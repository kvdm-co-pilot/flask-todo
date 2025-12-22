# test_todo_management.py

from app import db
from app.models import Todo
import pytest

# Fixture to set up a Todo instance
@pytest.fixture
def todo():
    return Todo(title="Sample Todo")

# Cleanup before each test
@pytest.fixture(autouse=True)
def setup_and_cleanup_database():
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()

# Test to validate the creation of a new Todo item with a valid title

def test_create_new_todo_valid_title_and_unique_id(todo):
    # Given
    expected_title = "Sample Todo"

    # When
    db.session.add(todo)
    db.session.commit()
    result_title = todo.title
    result_id = todo.id

    # Then
    assert result_title == expected_title, "Todo title should be correctly set"
    assert result_id is not None, "Todo ID should be set after saving to the database"

# Test to ensure a title with minimum length is accepted

def test_boundary_title_length_min_value_ensure_title_with_1_character_accepted():
    # Given
    todo = Todo(title="T")
    expected_title_length = 1

    # When
    db.session.add(todo)
    db.session.commit()
    result_title_length = len(todo.title)

    # Then
    assert result_title_length == expected_title_length, "Todo title should accept 1 character minimum"

# Test for retrieving a Todo by existing ID

def test_functional_retrieve_todo_by_id_existing_id_returns_correct_todo(todo):
    # Setup: Save todo to the database to get an ID
    db.session.add(todo)
    db.session.commit()
    expected_id = todo.id

    # When
    retrieved_todo = Todo.query.get(expected_id)

    # Then
    assert retrieved_todo is not None, "Retrieved Todo should not be None"
    assert retrieved_todo.title == todo.title, "Retrieved Todo should have the correct title"

# Test to confirm deletion of a Todo by ID

def test_functional_delete_todo_by_id_existing_id_confirms_deletion(todo):
    # Setup: Save todo to the database to get an ID
    db.session.add(todo)
    db.session.commit()
    todo_id = todo.id

    # When
    db.session.delete(todo)
    db.session.commit()
    deleted_todo = Todo.query.get(todo_id)

    # Then
    assert deleted_todo is None, "Deleted Todo should not be retrievable from the database"

# Test for handling error when trying to retrieve a non-existent Todo

def test_functional_retrieve_non_existent_todo_by_id_error_returned():
    # Given
    non_existent_id = 9999

    # When
    retrieved_todo = Todo.query.get(non_existent_id)

    # Then
    assert retrieved_todo is None, "Retrieving non-existent Todo should return None"

# Test to ensure creation of a Todo item with special characters in the title

def test_functional_add_todo_special_characters():
    # Given
    special_char_title = "Todo - 123!@#"
    todo = Todo(title=special_char_title)

    # When
    db.session.add(todo)
    db.session.commit()
    retrieved_todo = Todo.query.get(todo.id)

    # Then
    assert retrieved_todo.title == special_char_title, "Todo title should correctly store special characters"
