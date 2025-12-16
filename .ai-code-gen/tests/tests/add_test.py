from app import app, db, Todo
from flask import request, render_template
import pytest

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()

class FunctionalAddTaskTest:

    def test_add_valid_task(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='Complete Homework'))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title='Complete Homework').first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'Complete Homework'

    def test_add_task_without_title(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=''))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 400
        assert b'Title is required' in data

    def test_add_duplicate_task_title(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Grocery Shopping'))
        response = test_client.post('/add', data=dict(title='Grocery Shopping'))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        # Assuming duplicates are allowed, but system warns
        assert status_code == 302
        assert b'Duplicate title warning' in data or Todo.query.filter_by(title='Grocery Shopping').count() == 2

    def test_add_task_title_exceeds_limit(self, test_client):
        # Given
        long_title = 'A' * 256
        response = test_client.post('/add', data=dict(title=long_title))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 400
        assert b'Title exceeds the character limit' in data

    def test_add_task_with_special_characters(self, test_client):
        # Given
        special_title = 'Task @ # $ % ^'
        response = test_client.post('/add', data=dict(title=special_title))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=special_title).first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == special_title

    def test_server_error_on_add_task(self, test_client):
        # Given - Simulate server error by mocking
        with pytest.raises(Exception, match='Server error, please try again later'):
            raise Exception('Server error, please try again later')

        # When
        response = test_client.post('/add', data=dict(title='New Task'))

        # Then
        status_code = response.status_code
        data = response.data
        assert status_code == 500
        assert b'Server error, please try again later' in data

class InvariantTodoItemTest:

    def test_verify_todo_item_has_title(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=''))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 400
        assert b'Title is required' in data

    def test_verify_unique_todo_id(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Task One'))
        test_client.post('/add', data=dict(title='Task Two'))

        # When
        id_one = Todo.query.filter_by(title='Task One').first().id
        id_two = Todo.query.filter_by(title='Task Two').first().id

        # Then
        assert id_one != id_two

class SecurityTaskTest:

    def test_add_task_sql_injection_prevention(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='DROP TABLE tasks;'))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 400
        assert b'SQL injection attempt detected' in data

    def test_add_task_xss_prevention(self, test_client):
        # Given
        xss_title = '<script>alert("XSS")</script>'
        response = test_client.post('/add', data=dict(title=xss_title))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 400
        assert b'XSS attempt detected' in data

class FailureRecoveryTest:

    def test_database_commit_failure_on_task_deletion(self, test_client):
        # Simulate database failure
        with pytest.raises(Exception, match='Database commit failed'):
            raise Exception('Database commit failed')

        # Given
        response = test_client.post('/delete', data=dict(id=1))

        # When
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 500
        assert b'Database commit failed' in data