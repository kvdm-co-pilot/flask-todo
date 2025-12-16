import pytest
from flask import url_for, redirect
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

@pytest.fixture
def mocker():
    from unittest.mock import patch
    return patch

class FunctionalAddNewTodoValidInputTest:
    def test_add_new_todo_valid_input(self, client):
        # Given
        data = {'title': 'Buy groceries', 'description': 'Milk, Bread, Eggs', 'status': 'Incomplete'}
        initial_count = db.session.query(Todo).count()

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).count() == initial_count + 1  # New todo added
        new_todo = db.session.query(Todo).filter_by(title='Buy groceries').first()
        assert new_todo is not None
        assert new_todo.description == 'Milk, Bread, Eggs'
        assert new_todo.status == 'Incomplete'

class FunctionalUpdateTodoValidInputTest:
    def test_update_todo_valid_input(self, client):
        # Given
        todo_item = Todo(title='Buy groceries', description='Milk, Bread, Eggs', status='Incomplete')
        db.session.add(todo_item)
        db.session.commit()
        data = {'title': 'Buy groceries and fruits', 'description': 'Milk, Bread, Eggs, Apples'}

        # When
        response = client.post(url_for('update', todo_id=todo_item.id), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.title == 'Buy groceries and fruits'
        assert updated_item.description == 'Milk, Bread, Eggs, Apples'

class FunctionalRedirectAfterAddTest:
    def test_redirect_after_add(self, client):
        # Given
        data = {'title': 'Complete assignment'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Redirect successful
        assert b'<title>Todo App</title>' in response.data

class FunctionalRedirectAfterUpdateTest:
    def test_redirect_after_update(self, client):
        # Given
        todo_item = Todo(title='Buy groceries', description='Milk, Bread, Eggs')
        db.session.add(todo_item)
        db.session.commit()
        data = {'title': 'Complete homework'}

        # When
        response = client.post(url_for('update', todo_id=todo_item.id), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Redirect successful
        assert b'<title>Todo App</title>' in response.data

class InvariantUniqueTodoIDTest:
    def test_unique_todo_id(self, client):
        # Given
        todo1 = Todo(title='Walk the dog')
        todo2 = Todo(title='Read a book')
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # Then
        assert todo1.id != todo2.id  # Unique IDs

class BoundaryTodoTitleMaxLengthTest:
    def test_todo_title_max_length(self, client):
        # Given
        data = {'title': 'A' * 101}  # 101 characters

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Error message expected

class InvariantTodoCompletionStatusBooleanTest:
    def test_todo_completion_status_boolean(self, client):
        # Given
        data = {'title': 'Test Todo', 'status': 'Completed'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Error message expected

class StateTransitionTodoCompletionStatusChangeTest:
    def test_todo_completion_status_change(self, client):
        # Given
        todo_item = Todo(title='Test Todo', status='Incomplete')
        db.session.add(todo_item)
        db.session.commit()

        # When
        client.post(url_for('update', todo_id=todo_item.id), data={'status': 'Complete'}, follow_redirects=True)
        client.post(url_for('update', todo_id=todo_item.id), data={'status': 'Incomplete'}, follow_redirects=True)

        # Then
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.status == 'Incomplete'

class StateTransitionTodoDeletionTest:
    def test_todo_deletion(self, client):
        # Given
        todo_item = Todo(title='Test Todo', status='Incomplete')
        db.session.add(todo_item)
        db.session.commit()
        initial_count = db.session.query(Todo).count()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).count() == initial_count - 1  # Todo deleted
        assert db.session.get(Todo, todo_item.id) is None

class BoundaryTodoTitleMinLengthTest:
    def test_todo_title_min_length(self, client):
        # Given
        data = {'title': 'A'}  # 1 character

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).filter_by(title='A').count() == 1

class BoundaryTodoTitleExactMaxLengthTest:
    def test_todo_title_exact_max_length(self, client):
        # Given
        data = {'title': 'A' * 100}  # 100 characters

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).filter_by(title='A' * 100).count() == 1

class BoundaryEmptyTodoTitleTest:
    def test_empty_todo_title(self, client):
        # Given
        data = {'title': ''}  # Empty string

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Error message expected

class BoundaryTodoIDAutoIncrementTest:
    def test_todo_id_auto_increment(self, client):
        # Given
        todo1 = Todo(title='Task 1')
        todo2 = Todo(title='Task 2')
        todo3 = Todo(title='Task 3')
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.add(todo3)
        db.session.commit()

        # Then
        assert todo1.id + 1 == todo2.id
        assert todo2.id + 1 == todo3.id

class SecuritySQLInjectionOnAddTest:
    def test_sql_injection_on_add(self, client):
        # Given
        data = {'title': 'DROP TABLE todos; --'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Input sanitized

class SecurityUnauthorizedTodoDeletionTest:
    def test_unauthorized_todo_deletion(self, client):
        # Given
        todo_item = Todo(title='Test Todo')
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=False)

        # Then
        assert response.status_code == 403  # Access denied
        assert db.session.get(Todo, todo_item.id) is not None

class FailureDatabaseCommitFailureOnAddTest:
    def test_database_commit_failure_on_add(self, mocker, client):
        # Given
        mocker.patch('app.db.session.commit', side_effect=Exception('Commit failed'))
        data = {'title': 'Network issue simulation'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 500  # Error handling
        assert b'Commit failed' in response.data

class FailureDatabaseCommitFailureOnUpdateTest:
    def test_database_commit_failure_on_update(self, mocker, client):
        # Given
        todo_item = Todo(title='Test Todo')
        db.session.add(todo_item)
        db.session.commit()
        mocker.patch('app.db.session.commit', side_effect=Exception('Commit failed'))

        # When
        response = client.post(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 500  # Error handling
        assert b'Commit failed' in response.data

class RecoveryRetryAfterDatabaseFailureTest:
    def test_retry_after_database_failure(self, mocker, client):
        # Given
        mocker.patch('app.db.session.commit', side_effect=[Exception('Commit failed'), None])
        data = {'title': 'Reconnect'}

        # When
        response = client.post(url_for('add'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200  # Retry successful
        assert db.session.query(Todo).filter_by(title='Reconnect').count() == 1

class CrossEntityTodoListRetrievalAccuracyTest:
    def test_todo_list_retrieval_accuracy(self, client):
        # Given
        todo1 = Todo(title='Walk the dog')
        todo2 = Todo(title='Read a book')
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # When
        response = client.get(url_for('list'), follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Walk the dog' in response.data
        assert b'Read a book' in response.data

class CrossEntityTodoUserConsistencyTest:
    def test_todo_user_consistency(self, client):
        # Given
        user_a_todo = Todo(title='User A Task', user_id=1)
        user_b_todo = Todo(title='User B Task', user_id=2)
        db.session.add(user_a_todo)
        db.session.add(user_b_todo)
        db.session.commit()

        # When
        response = client.get(url_for('user_todos', user_id=1), follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'User A Task' in response.data
        assert b'User B Task' not in response.data