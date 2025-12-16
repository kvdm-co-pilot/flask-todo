import pytest
from app import app, db, Todo
from flask import url_for
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_functional_toggle_completion_status_existing_incomplete_todo(client):
    # Given
    todo_item = Todo(id=1, title='Incomplete Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=1), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, 1)
    assert updated_item.complete is True
    assert b'Home Page' in response.data


def test_functional_toggle_completion_status_existing_complete_todo(client):
    # Given
    todo_item = Todo(id=2, title='Complete Todo', complete=True)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=2), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, 2)
    assert updated_item.complete is False
    assert b'Home Page' in response.data


def test_functional_toggle_completion_status_non_existent_todo(client):
    # Given
    non_existent_id = 999

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=non_existent_id), follow_redirects=True)

    # Then
    assert response.status_code == 404
    assert b'Error' in response.data


def test_functional_toggle_completion_status_with_database_commit_failure(client, mocker: MockerFixture):
    # Given
    todo_item = Todo(id=3, title='Todo With Commit Failure', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    mocker.patch('app.db.session.commit', side_effect=Exception('Commit failed'))

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=3), follow_redirects=True)

    # Then
    assert response.status_code == 500
    updated_item = db.session.get(Todo, 3)
    assert updated_item.complete is False
    assert b'Error' in response.data


def test_functional_toggle_completion_status_special_characters_in_todo(client):
    # Given
    todo_item = Todo(id=4, title='Special @#$% Characters', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=4), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, 4)
    assert updated_item.complete is True
    assert b'Special @#$% Characters' in response.data


def test_invariant_verify_unique_todo_id(client):
    # Given - setup multiple todos with unique IDs
    todo_item_1 = Todo(id=5, title='Unique ID Todo 1', complete=False)
    todo_item_2 = Todo(id=6, title='Unique ID Todo 2', complete=True)
    db.session.add(todo_item_1)
    db.session.add(todo_item_2)
    db.session.commit()

    # When - try adding a new todo with a duplicate ID
    duplicate_todo = Todo(id=5, title='Duplicate ID Todo', complete=False)
    try:
        db.session.add(duplicate_todo)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e)

    # Then
    assert Todo.query.count() == 2  # No new todo added
    assert 'UNIQUE constraint failed' in error_message


def test_boundary_verify_todo_title_max_length(client):
    # Given
    long_title = 'A' * 256
    todo_item = Todo(title=long_title, complete=False)
    db.session.add(todo_item)

    # When
    with pytest.raises(ValueError) as e:
        db.session.commit()

    # Then
    assert 'title length exceeded' in str(e.value)


def test_negative_verify_todo_completion_status_boolean(client):
    # Given
    invalid_status = 'string'
    todo_item = Todo(id=7, title='Invalid Completion Status Todo', complete=invalid_status)

    # When
    with pytest.raises(ValueError) as e:
        db.session.add(todo_item)
        db.session.commit()

    # Then
    assert 'Completion status must be boolean' in str(e.value)


def test_state_transition_toggle_completion_status_incomplete_to_complete(client):
    # Given
    todo_item = Todo(id=1, title='Incomplete Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=1), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, 1)
    assert updated_item.complete is True
    assert b'Home Page' in response.data


def test_state_transition_toggle_completion_status_complete_to_incomplete(client):
    # Given
    todo_item = Todo(id=2, title='Complete Todo', complete=True)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=2), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, 2)
    assert updated_item.complete is False
    assert b'Home Page' in response.data


def test_negative_state_transition_toggle_completion_status_existing_to_deleted(client):
    # Given
    todo_item = Todo(id=5, title='Deleted Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    db.session.delete(todo_item)
    db.session.commit()
    response = client.get(url_for('toggle_completion_status', todo_id=5), follow_redirects=True)

    # Then
    assert response.status_code == 404
    assert b'Error: Todo not found' in response.data


def test_boundary_todo_title_min_length(client):
    # Given
    short_title = 'a'
    todo_item = Todo(title=short_title, complete=False)
    db.session.add(todo_item)

    # When
    db.session.commit()

    # Then
    assert Todo.query.filter_by(title='a').count() == 1


def test_boundary_todo_title_max_length_unique(client):
    # Given
    max_length_title = 'A' * 255
    todo_item = Todo(title=max_length_title, complete=False)
    db.session.add(todo_item)

    # When
    db.session.commit()

    # Then
    assert Todo.query.filter_by(title=max_length_title).count() == 1


def test_boundary_todo_title_empty(client):
    # Given
    empty_title = ''
    todo_item = Todo(title=empty_title, complete=False)

    # When
    with pytest.raises(ValueError) as e:
        db.session.add(todo_item)
        db.session.commit()

    # Then
    assert 'Title cannot be empty' in str(e.value)


def test_boundary_todo_id_positive_integer(client):
    # Given
    negative_id = -1
    todo_item = Todo(id=negative_id, title='Negative ID Todo', complete=False)

    # When
    with pytest.raises(ValueError) as e:
        db.session.add(todo_item)
        db.session.commit()

    # Then
    assert 'ID must be positive integer' in str(e.value)


def test_boundary_todo_completion_status_boolean_values(client):
    # Given
    invalid_status = 2
    todo_item = Todo(id=8, title='Invalid Status Todo', complete=invalid_status)

    # When
    with pytest.raises(ValueError) as e:
        db.session.add(todo_item)
        db.session.commit()

    # Then
    assert 'Completion status must be boolean' in str(e.value)


def test_error_security_todo_addition_post_request_injection(client):
    # Given
    injection_payload = {'title': "'); DROP TABLE todos; --"}

    # When
    response = client.post(url_for('add'), data=injection_payload, follow_redirects=True)

    # Then
    assert response.status_code == 400
    assert b'Error: SQL Injection detected' in response.data


def test_negative_security_todo_deletion_url_manipulation_unauthorized_access(client):
    # Given
    todo_item = Todo(id=9, title='Secure Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('delete', todo_id=999), follow_redirects=True)

    # Then
    assert response.status_code == 403
    assert b'Error: Unauthorized access' in response.data


def test_error_failure_recovery_toggle_completion_status_database_commit_failure(client, mocker: MockerFixture):
    # Given
    todo_item = Todo(id=10, title='Recovery Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    mocker.patch('app.db.session.commit', side_effect=Exception('Commit failed'))

    # When
    response = client.get(url_for('toggle_completion_status', todo_id=10), follow_redirects=True)

    # Then
    assert response.status_code == 500
    updated_item = db.session.get(Todo, 10)
    assert updated_item.complete is False
    assert b'Error: Database commit failed' in response.data


def test_error_failure_recovery_toggle_completion_status_interrupted_operation(client):
    # Given
    todo_item = Todo(id=11, title='Interrupted Operation Todo', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    try:
        # Simulate interruption
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        pass

    response = client.get(url_for('toggle_completion_status', todo_id=11), follow_redirects=True)

    # Then
    assert response.status_code == 500
    assert b'Error: Operation interrupted' in response.data


def test_exact_cross_entity_todo_list_retrieval_accurate_display_in_ui(client):
    # Given
    todo_item_1 = Todo(id=12, title='Cross Entity Todo 1', complete=False)
    todo_item_2 = Todo(id=13, title='Cross Entity Todo 2', complete=True)
    db.session.add(todo_item_1)
    db.session.add(todo_item_2)
    db.session.commit()

    # When
    client.get(url_for('toggle_completion_status', todo_id=12), follow_redirects=True)
    client.get(url_for('toggle_completion_status', todo_id=13), follow_redirects=True)
    response = client.get(url_for('home'), follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert b'Cross Entity Todo 1' in response.data
    assert b'Cross Entity Todo 2' in response.data
    assert b'Complete' in response.data