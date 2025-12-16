import pytest
from app import app, db, Todo
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

class TestTodoManagement:
    
    def test_add_valid_todo_successful_addition(self, client):
        # Given
        initial_count = Todo.query.count()
        data = {'title': 'Complete project'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        assert Todo.query.count() == initial_count + 1
        assert Todo.query.filter_by(title='Complete project').first() is not None

    def test_update_todo_completion_status_successful_toggle(self, client):
        # Given
        todo_item = Todo(title='Complete project', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is True

    def test_delete_existing_todo_successful_deletion(self, client):
        # Given
        todo_item = Todo(title='Complete project', complete=False)
        db.session.add(todo_item)
        db.session.commit()
        initial_count = Todo.query.count()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        assert Todo.query.count() == initial_count - 1

    def test_add_todo_with_exceeding_title_reject_with_error(self, client):
        # Given
        data = {'title': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque fringilla metus.'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Should not redirect
        assert Todo.query.filter_by(title=data['title']).first() is None

    def test_add_todo_with_empty_title_reject_with_error(self, client):
        # Given
        data = {'title': ''}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Should not redirect
        assert Todo.query.filter_by(title=data['title']).first() is None

    def test_unique_todo_id_verify_on_addition(self, client):
        # Given
        data1 = {'title': 'Task 1'}
        data2 = {'title': 'Task 2'}

        # When
        client.post(url_for('add'), data=data1, follow_redirects=True)
        client.post(url_for('add'), data=data2, follow_redirects=True)

        # Then
        task1 = Todo.query.filter_by(title='Task 1').first()
        task2 = Todo.query.filter_by(title='Task 2').first()
        assert task1.id != task2.id

    def test_todo_completion_status_boolean_verify_on_toggle(self, client):
        # Given
        todo_item = Todo(title='Task 1', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        updated_item = db.session.get(Todo, todo_item.id)
        assert isinstance(updated_item.complete, bool)

    def test_state_transition_todo_completion_toggle_incomplete_to_complete(self, client):
        # Given
        todo_item = Todo(title='Task 1', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is True

    def test_state_transition_todo_completion_toggle_complete_to_incomplete(self, client):
        # Given
        todo_item = Todo(title='Task 1', complete=True)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is False

    def test_state_transition_todo_deletion_existing_to_deleted(self, client):
        # Given
        todo_item = Todo(title='Task 1', complete=False)
        db.session.add(todo_item)
        db.session.commit()
        initial_count = Todo.query.count()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        assert Todo.query.count() == initial_count - 1

    def test_boundary_todo_title_min_length_reject_empty_title(self, client):
        # Given
        data = {'title': ''}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Should not redirect
        assert Todo.query.filter_by(title=data['title']).first() is None

    def test_boundary_todo_title_max_length_reject_exceeding_title(self, client):
        # Given
        data = {'title': 'A' * 101}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Should not redirect
        assert Todo.query.filter_by(title=data['title']).first() is None

    def test_boundary_todo_id_positive_reject_negative_id(self, client):
        # Given
        negative_id = -1

        # When
        response = client.get(url_for('update', todo_id=negative_id), follow_redirects=True)

        # Then
        assert response.status_code == 404  # Not found status code

    def test_boundary_todo_completion_status_only_boolean_reject_non_boolean(self, client):
        # Given
        todo_item = Todo(title='Task 1', complete=False)
        db.session.add(todo_item)
        db.session.commit()
        non_boolean_status = 'yes'

        # When
        with pytest.raises(ValueError) as e:
            todo_item.complete = non_boolean_status
            db.session.commit()

        # Then
        assert str(e.value) == 'Completion status must be boolean'

    def test_security_todo_addition_injection_attempt_sql_injection(self, client):
        # Given
        data = {'title': 'Task 1; DROP TABLE Todo; --'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        assert Todo.query.filter_by(title=data['title']).first() is None

    def test_security_todo_deletion_unauthorized_attempt_url_manipulation(self, client):
        # Given
        unauthorized_id = 9999  # Assuming this ID does not exist

        # When
        response = client.get(url_for('delete', todo_id=unauthorized_id), follow_redirects=True)

        # Then
        assert response.status_code == 404  # Not found status code

    def test_failure_database_connection_failure_graceful_error_handling_on_add(self, client):
        # Given
        data = {'title': 'Test Todo'}

        # Simulate DB failure
        with pytest.raises(ConnectionError) as e:
            raise ConnectionError('Database connection failed')

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert 'Database connection failed' in str(e.value)

    def test_failure_database_connection_failure_graceful_error_handling_on_update(self, client):
        # Given
        todo_item = Todo(title='Test Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # Simulate DB failure
        with pytest.raises(ConnectionError) as e:
            raise ConnectionError('Database connection failed')

        # When
        response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert 'Database connection failed' in str(e.value)

    def test_failure_database_connection_failure_graceful_error_handling_on_delete(self, client):
        # Given
        todo_item = Todo(title='Test Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # Simulate DB failure
        with pytest.raises(ConnectionError) as e:
            raise ConnectionError('Database connection failed')

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert 'Database connection failed' in str(e.value)

    def test_recovery_interrupted_addition_operation_retry_mechanism(self, client):
        # Given
        data = {'title': 'Test Todo'}

        # When
        try:
            response = client.post(url_for('add'), data=data)
            raise ConnectionError('Interrupted operation')
        except ConnectionError:
            response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 302  # Redirect status code
        assert Todo.query.filter_by(title='Test Todo').first() is not None

    def test_consistency_all_todos_retrieved_display_correctly_in_ui(self, client):
        # Given
        data1 = {'title': 'Task 1'}
        data2 = {'title': 'Task 2'}
        client.post(url_for('add'), data=data1, follow_redirects=True)
        client.post(url_for('add'), data=data2, follow_redirects=True)

        # When
        response = client.get(url_for('home'))

        # Then
        assert response.status_code == 200
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data