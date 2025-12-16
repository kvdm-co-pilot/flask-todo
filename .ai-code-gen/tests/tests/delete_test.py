# test_toggle_completion_status.py

# Import statements
import pytest
from app import app, db, Todo
from flask import url_for

# Test package convention: test_<filename>.py
# Use Pytest as the testing framework

class TestToggleCompletionStatus:
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

    def test_toggle_completion_status_valid_incomplete_to_complete(self, test_client):
        # Given
        todo = Todo(id=1, complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

    def test_toggle_completion_status_valid_complete_to_incomplete(self, test_client):
        # Given
        todo = Todo(id=2, complete=True)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is False
        assert response.status_code == 200

    def test_toggle_completion_status_non_existent_task_displays_error(self, test_client):
        # When
        response = test_client.get('/update/3', follow_redirects=True)

        # Then
        assert b'Todo item not found.' in response.data

    def test_unique_todo_id_maintained_after_toggle(self, test_client):
        # Given
        todo = Todo(id=4, complete=True)
        db.session.add(todo)
        db.session.commit()

        # When
        test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.id == 4

    def test_task_title_length_limit_not_affected_by_toggle(self, test_client):
        # Given
        todo = Todo(id=5, title='Sample Task Title', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert len(updated_todo.title) <= 255

    def test_toggle_completion_valid_state_change_incomplete_to_complete(self, test_client):
        # Given
        todo = Todo(id=6, complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True

    def test_toggle_completion_valid_state_change_complete_to_incomplete(self, test_client):
        # Given
        todo = Todo(id=7, complete=True)
        db.session.add(todo)
        db.session.commit()

        # When
        test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is False

    def test_toggle_completion_non_existent_task_error(self, test_client):
        # When
        response = test_client.get('/update/8', follow_redirects=True)

        # Then
        assert b'Todo item not found.' in response.data

    def test_toggle_completion_boundary_value_id_zero(self, test_client):
        # Given
        todo = Todo(id=0, complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

    def test_toggle_completion_max_integer_id(self, test_client):
        # Given
        max_int = 2147483647  # Assuming 32-bit integer
        todo = Todo(id=max_int, complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

    def test_toggle_completion_non_boolean_complete_status(self, test_client):
        # Given
        todo = Todo(id=9, complete='yes')
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b"Invalid complete status" in response.data

    def test_toggle_completion_sql_injection_prevented(self, test_client):
        # Given
        todo_id = '1; DROP TABLE todos;'

        # When
        response = test_client.get(f'/update/{todo_id}', follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b"SQL injection attempt detected" in response.data

    def test_toggle_completion_xss_prevented(self, test_client):
        # Given
        todo_id = '<script>alert(1);</script>'

        # When
        response = test_client.get(f'/update/{todo_id}', follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b"XSS attempt detected" in response.data

    def test_toggle_completion_csrf_protected(self, test_client):
        # Given
        todo = Todo(id=10, complete=True)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}?csrf_token=invalid', follow_redirects=True)

        # Then
        assert response.status_code == 403
        assert b"Invalid CSRF token" in response.data

    def test_toggle_completion_database_update_failure(self, test_client):
        # Given
        todo = Todo(id=11, complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate database failure
        db.session.rollback()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        assert response.status_code == 500
        assert b"Database error occurred" in response.data

    def test_toggle_completion_network_failure(self, test_client):
        # Given
        todo = Todo(id=12, complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate network failure
        app.config['TESTING'] = False  # Temporary disable testing

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        assert response.status_code == 503
        assert b"Network error occurred" in response.data

    def test_todo_list_retrieval_accurate_display_after_toggle(self, test_client):
        # Given
        todo = Todo(id=13, complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        response = test_client.get('/')
        assert b"Todo List" in response.data
        assert b"Complete" in response.data
