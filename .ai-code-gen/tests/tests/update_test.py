# test_todo_functionality.py

# Import statements
import pytest
from app import app, db, Todo
from flask import url_for

# Test class derived from 'Functional' entity in test plan
class TestFunctionalTodoApp:
    @pytest.fixture(scope='module')
    def test_client(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.test_client() as testing_client:
            with app.app_context():
                db.create_all()
                yield testing_client
                db.drop_all()

    def test_add_new_todo_valid_details(self, test_client):
        # Given
        new_todo_data = {'title': 'Buy groceries', 'description': 'Milk, Bread, Eggs'}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Buy groceries' in response.data

    def test_update_existing_todo_valid_id_and_details(self, test_client):
        # Given
        todo = Todo.query.first()
        updated_data = {'title': 'Read book', 'description': 'Chapter 1-3'}

        # When
        response = test_client.post(f'/update/{todo.id}', data=updated_data, follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert response.status_code == 200
        assert updated_todo.title == 'Read book'

    def test_add_todo_missing_details(self, test_client):
        # Given
        incomplete_data = {'title': '', 'description': 'Email report'}

        # When
        response = test_client.post('/add', data=incomplete_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Title is required' in response.data

    def test_update_todo_non_existent_id(self, test_client):
        # Given
        non_existent_id = 999
        update_data = {'title': 'Meeting prep', 'description': 'Agenda review'}

        # When
        response = test_client.post(f'/update/{non_existent_id}', data=update_data, follow_redirects=True)

        # Then
        assert response.status_code == 404
        assert b'Todo item does not exist' in response.data

    def test_unique_todo_id_invariant(self, test_client):
        # Given
        todos = [
            {'title': 'Task 1', 'description': 'Description 1'},
            {'title': 'Task 2', 'description': 'Description 2'}
        ]
        for todo_data in todos:
            test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        todo_ids = {todo.id for todo in Todo.query.all()}
        assert len(todo_ids) == len(todos)

    def test_task_title_length_limit_boundary(self, test_client):
        # Given
        max_length_title = 'A' * 255
        todo_data = {'title': max_length_title, 'description': 'Test maximum length title'}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert max_length_title.encode() in response.data

    def test_toggle_task_completion_incomplete_to_complete(self, test_client):
        # Given
        todo = Todo.query.first()
        toggle_data = {'complete': True}

        # When
        response = test_client.post(f'/toggle/{todo.id}', data=toggle_data, follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert response.status_code == 200
        assert updated_todo.complete is True

    def test_delete_task_task_exists_to_task_deleted(self, test_client):
        # Given
        todo = Todo.query.first()

        # When
        response = test_client.get(f'/delete/{todo.id}', follow_redirects=True)

        # Then
        deleted_todo = Todo.query.filter_by(id=todo.id).first()
        assert deleted_todo is None
        assert response.status_code == 200

    def test_security_add_task_sql_injection_check(self, test_client):
        # Given
        injection_data = {'title': "Test'); DROP TABLE todos; --", 'description': 'SQL injection test'}

        # When
        response = test_client.post('/add', data=injection_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'SQL injection detected' in response.data

    def test_security_add_task_xss_check(self, test_client):
        # Given
        xss_data = {'title': '<script>alert("XSS")</script>', 'description': 'XSS test'}

        # When
        response = test_client.post('/add', data=xss_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'XSS detected' in response.data

    def test_security_delete_task_broken_auth_check(self, test_client):
        # Given
        unauthenticated_request_id = 6

        # When
        response = test_client.get(f'/delete/{unauthenticated_request_id}', follow_redirects=True)

        # Then
        assert response.status_code == 403
        assert b'Authentication required' in response.data

    def test_security_delete_task_csrf_check(self, test_client):
        # Given
        csrf_attempt_id = 7

        # When
        response = test_client.post(f'/delete/{csrf_attempt_id}', headers={'X-CSRF-Token': 'invalid'}, follow_redirects=True)

        # Then
        assert response.status_code == 403
        assert b'CSRF protection triggered' in response.data

    def test_failure_add_new_task_database_write_failure(self, test_client):
        # Given
        failing_data = {'title': 'Network test', 'description': 'Database write failure simulation'}

        # Simulate failure
        db.session.commit = lambda: (_ for _ in ()).throw(Exception('Write failure'))

        # When
        response = test_client.post('/add', data=failing_data, follow_redirects=True)

        # Then
        assert response.status_code == 500
        assert b'Write failure' in response.data

    def test_failure_add_new_task_network_issue_during_redirect(self, test_client):
        # Given
        network_issue_data = {'title': 'Network test', 'description': 'Redirect failure simulation'}

        # Simulate network failure
        app.redirect = lambda url: (_ for _ in ()).throw(Exception('Redirect failure'))

        # When
        response = test_client.post('/add', data=network_issue_data, follow_redirects=True)

        # Then
        assert response.status_code == 500
        assert b'Redirect failure' in response.data

    def test_cross_entity_task_list_retrieval_all_tasks_displayed_correctly(self, test_client):
        # Given
        test_client.post('/add', data={'title': 'Task 1', 'description': 'Description 1'}, follow_redirects=True)

        # When
        response = test_client.get('/tasks', follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Task 1' in response.data

    def test_cross_entity_todo_user_interface_retrieved_tasks_match_database(self, test_client):
        # Given
        Todo.query.delete()
        db.session.commit()
        test_client.post('/add', data={'title': 'UI Test Task', 'description': 'UI Test Description'}, follow_redirects=True)

        # When
        response = test_client.get('/tasks', follow_redirects=True)

        # Then
        task_in_db = Todo.query.first()
        assert response.status_code == 200
        assert task_in_db.title.encode() in response.data
