# test_functional_add_valid_task.py

# Package declaration
import pytest
from app import create_app, db
from app.models import Todo

# Given-When-Then structured test cases

@pytest.fixture
def app_context():
    """Fixture to create app context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture
def client(app_context):
    """Fixture to create test client"""
    return app_context.test_client()

@pytest.fixture
def setup_database(app_context):
    """Fixture to set up database for testing"""
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


def test_add_valid_task(client, setup_database):
    """
    Scenario: Add a New Todo Task (Happy Path)
    Test adding a task with a valid title and description.
    """
    # Given
    task_title = 'Buy Groceries'
    task_description = 'Purchase milk, eggs, and bread.'

    # When
    response = client.post('/todos', data={'title': task_title, 'description': task_description})

    # Then
    assert response.status_code == 200
    assert bytes(task_title, 'utf-8') in response.data
    assert bytes(task_description, 'utf-8') in response.data
    with app_context:
        todo = Todo.query.filter_by(title=task_title).first()
        assert todo is not None
        assert todo.description == task_description


def test_add_empty_task(client, setup_database):
    """
    Scenario: Add a Todo Task with Empty Fields (Error Condition)
    Attempt to add a task with empty fields and expect an error.
    """
    # Given
    task_title = ''
    task_description = ''

    # When
    response = client.post('/todos', data={'title': task_title, 'description': task_description})

    # Then
    assert response.status_code == 400  # Assuming 400 for validation error
    assert b'Please enter required fields' in response.data


def test_add_max_length_task(client, setup_database):
    """
    Scenario: Add a Todo Task with Maximum Field Length (Boundary Value)
    Add a task with maximum length title and description.
    """
    # Given
    task_title = 'A' * 100
    task_description = 'B' * 255

    # When
    response = client.post('/todos', data={'title': task_title, 'description': task_description})

    # Then
    assert response.status_code == 200
    with app_context:
        todo = Todo.query.filter_by(title=task_title).first()
        assert todo is not None
        assert todo.description == task_description


def test_add_task_sql_injection(client, setup_database):
    """
    Scenario: Attempt SQL injection via task title and ensure prevention.
    """
    # Given
    task_title = 'DROP TABLE tasks;'
    task_description = 'Attempt SQL injection.'

    # When
    response = client.post('/todos', data={'title': task_title, 'description': task_description})

    # Then
    assert response.status_code == 400
    assert b'SQL injection attempt prevented' in response.data


def test_add_task_xss(client, setup_database):
    """
    Scenario: Attempt cross-site scripting via task title and ensure prevention.
    """
    # Given
    task_title = '<script>alert(1);</script>'
    task_description = 'Attempt XSS.'

    # When
    response = client.post('/todos', data={'title': task_title, 'description': task_description})

    # Then
    assert response.status_code == 400
    assert b'XSS attempt sanitized' in response.data


def test_delete_task_unauthorized_removal(client, setup_database):
    """
    Scenario: Verify unauthorized task deletion is not possible.
    """
    # Given
    task_title = 'Complete Assignment'
    client.post('/todos', data={'title': task_title, 'description': 'Valid description.'})

    # When
    response = client.post('/todos/delete', data={'title': task_title, 'user': 'unauthorized'})

    # Then
    assert response.status_code == 403
    assert b'Unauthorized deletion attempt prevented' in response.data
    with app_context:
        todo = Todo.query.filter_by(title=task_title).first()
        assert todo is not None  # Task should still exist


