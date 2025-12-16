import pytest
from myproject.app import create_app, db
from myproject.models import Todo

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_toggle_completion_status_valid_todo_id(client):
    # Given
    todo_data = {'title': 'Incomplete Todo', 'complete': False}
    response = client.post('/todos', json=todo_data)
    todo_id = response.get_json()['id']

    # When
    response = client.post(f'/todos/{todo_id}/toggle')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    todo = Todo.query.filter_by(id=todo_id).first()
    assert todo.complete is True


def test_toggle_completion_status_valid_todo_id_already_complete(client):
    # Given
    todo_data = {'title': 'Complete Todo', 'complete': True}
    response = client.post('/todos', json=todo_data)
    todo_id = response.get_json()['id']

    # When
    response = client.post(f'/todos/{todo_id}/toggle')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    todo = Todo.query.filter_by(id=todo_id).first()
    assert todo.complete is False


def test_toggle_completion_status_non_existing_todo_id(client):
    # Given
    non_existing_id = 789

    # When
    response = client.post(f'/todos/{non_existing_id}/toggle')

    # Then
    assert response.status_code == 404
    error_message = response.get_json()['error']
    assert error_message == 'Item not found'
    assert response.headers['Location'] == '/home'


def test_toggle_completion_status_boundary_id_value_zero(client):
    # Given
    todo_data = {'title': 'Boundary Todo', 'complete': False}
    response = client.post('/todos', json=todo_data)
    todo_id = 0  # Assuming 0 is valid

    # When
    response = client.post(f'/todos/{todo_id}/toggle')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    todo = Todo.query.filter_by(id=todo_id).first()
    assert todo.complete is True


def test_toggle_completion_status_boundary_id_value_max_integer(client):
    # Given
    max_int_id = 2147483647
    todo_data = {'title': 'Max Integer Todo', 'complete': True}
    response = client.post('/todos', json=todo_data)
    todo_id = response.get_json()['id']

    # When
    response = client.post(f'/todos/{todo_id}/toggle')

    # Then
    assert response.status_code == 302
    assert response.headers['Location'] == '/home'
    todo = Todo.query.filter_by(id=todo_id).first()
    assert todo.complete is False