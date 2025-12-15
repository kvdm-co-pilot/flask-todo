# test_toggle_completion.py

# Package declaration
import pytest
from app import create_app, db
from app.models import Todo

# Setup and Teardown
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    with app.app_context():
        db.drop_all()

@pytest.fixture
def setup_todos(client):
    with client.application.app_context():
        todos = [
            Todo(id=1, title='Task 1', complete=False),
            Todo(id=2, title='Task 2', complete=True),
            Todo(id=4, title='Task with exactly 255 characters' + 'x' * 225, complete=False),
            Todo(id=5, title='Task 5', complete=False),
            Todo(id=6, title='Task 6', complete=True),
            Todo(id=8, title='Max length title' + 'x' * 240, complete=False),
            Todo(id=9, title='Task 9', complete=False),
            Todo(id=10, title='Task 10', complete=False),
            Todo(id=11, title='Task 11', complete=False),
            Todo(id=12, title='Task 12', complete=False)
        ]
        db.session.bulk_save_objects(todos)
        db.session.commit()

# Test cases

def test_toggle_completion_status_valid_todo_id(client, setup_todos):
    # Given
    todo_id = 1
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is False

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_completion_status_already_completed_todo(client, setup_todos):
    # Given
    todo_id = 2
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is True

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is False


def test_toggle_completion_status_invalid_todo_id(client):
    # Given
    todo_id = 999

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 404
    assert b'Todo item does not exist' in response.data


def test_verify_unique_task_id_on_toggle(client, setup_todos):
    # Given
    todo_ids = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12]
    with client.application.app_context():
        todos = Todo.query.all()
        assert len(todos) == len(set(todo_ids))


def test_verify_task_title_length_on_toggle(client, setup_todos):
    # Given
    todo_id = 4
    with client.application.app_context():
        todo = Todo.query.filter_by(id=todo_id).first()
        assert len(todo.title) == 255

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_task_completion_from_incomplete_to_complete(client, setup_todos):
    # Given
    todo_id = 5
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is False

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_task_completion_from_complete_to_incomplete(client, setup_todos):
    # Given
    todo_id = 6
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is True

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is False


def test_toggle_completion_with_boundary_value_for_id(client, setup_todos):
    # Given
    todo_id = 0
    with client.application.app_context():
        todo = Todo(id=todo_id, title='Boundary Task', complete=False)
        db.session.add(todo)
        db.session.commit()

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_completion_with_empty_task_title(client, setup_todos):
    # Given
    todo_id = 7
    with client.application.app_context():
        todo = Todo(id=todo_id, title='', complete=False)
        db.session.add(todo)
        db.session.commit()

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_completion_with_max_length_task_title(client, setup_todos):
    # Given
    todo_id = 8
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert len(todo_before.title) == 256

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_toggle_completion_against_sql_injection(client):
    # Given
    todo_id = '1 OR 1=1'

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 400
    assert b'SQL injection detected' in response.data


def test_toggle_completion_against_cross_site_scripting(client):
    # Given
    todo_id = '<script>alert("xss")</script>'

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 400
    assert b'Cross-site scripting detected' in response.data


def test_toggle_completion_against_url_manipulation(client):
    # Given
    todo_id = '999999999999999999999999'

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 400
    assert b'Invalid URL detected' in response.data


def test_toggle_completion_against_session_hijacking(client):
    # Given
    with client.session_transaction() as session:
        session['user_id'] = 'manipulated_user_id'

    # When
    response = client.post('/toggle_completion/1')

    # Then
    assert response.status_code == 403
    assert b'Session hijacking detected' in response.data


def test_toggle_completion_with_database_commit_failure(client, setup_todos):
    # Given
    todo_id = 9
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is False

    # Force a commit failure
    db.session.rollback()

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 500
    assert b'Database commit failed' in response.data


def test_toggle_completion_with_network_failure_during_redirect(client, setup_todos):
    # Given
    todo_id = 10
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        assert todo_before.complete is False

    # Simulate network failure
    client.application.config['NETWORK_FAILURE'] = True

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 500
    assert b'Network failure during redirect' in response.data


def test_verify_task_id_mapping_on_toggle_completion(client, setup_todos):
    # Given
    todo_id = 11

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.complete is True


def test_verify_database_entry_consistency_after_toggle(client, setup_todos):
    # Given
    todo_id = 12
    with client.application.app_context():
        todo_before = Todo.query.filter_by(id=todo_id).first()
        expected_title = todo_before.title

    # When
    response = client.post(f'/toggle_completion/{todo_id}')

    # Then
    assert response.status_code == 302
    with client.application.app_context():
        todo_after = Todo.query.filter_by(id=todo_id).first()
        assert todo_after.title == expected_title
        assert todo_after.complete is True
