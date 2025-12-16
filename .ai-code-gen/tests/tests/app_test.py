from app import app, db, Todo
import pytest

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client


def test_add_new_task_with_valid_title(test_client):
    # Given
    response = test_client.post('/add', data=dict(title='Buy groceries'))

    # When
    status_code = response.status_code
    new_todo = Todo.query.filter_by(title='Buy groceries').first()

    # Then
    assert status_code == 302
    assert new_todo is not None
    assert new_todo.title == 'Buy groceries'
    assert new_todo.complete is False


def test_update_task_completion_status(test_client):
    # Given
    test_client.post('/add', data=dict(title='Read book'))
    todo = Todo.query.filter_by(title='Read book').first()

    # When
    response = test_client.get(f'/update/{todo.id}')
    updated_todo = Todo.query.filter_by(id=todo.id).first()

    # Then
    assert response.status_code == 302
    assert updated_todo.complete is True


def test_delete_existing_task(test_client):
    # Given
    test_client.post('/add', data=dict(title='Pay bills'))
    todo = Todo.query.filter_by(title='Pay bills').first()

    # When
    response = test_client.get(f'/delete/{todo.id}')
    deleted_todo = Todo.query.filter_by(id=todo.id).first()

    # Then
    assert response.status_code == 302
    assert deleted_todo is None


def test_add_task_with_empty_title(test_client):
    # Given
    response = test_client.post('/add', data=dict(title=''))

    # When
    status_code = response.status_code
    new_todo = Todo.query.filter_by(title='').first()

    # Then
    assert status_code == 400  # Assuming the system returns a 400 error for invalid input
    assert new_todo is None


def test_add_task_with_maximum_title_length(test_client):
    max_length_title = 'a' * 100
    # Given
    response = test_client.post('/add', data=dict(title=max_length_title))

    # When
    status_code = response.status_code
    new_todo = Todo.query.filter_by(title=max_length_title).first()

    # Then
    assert status_code == 302
    assert new_todo is not None
    assert new_todo.title == max_length_title


def test_add_task_with_title_length_exceeding_maximum(test_client):
    exceeding_length_title = 'a' * 101
    # Given
    response = test_client.post('/add', data=dict(title=exceeding_length_title))

    # When
    status_code = response.status_code
    new_todo = Todo.query.filter_by(title=exceeding_length_title).first()

    # Then
    assert status_code == 400  # Assuming the system returns a 400 error for invalid input
    assert new_todo is None