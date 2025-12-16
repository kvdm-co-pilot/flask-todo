# Import statements
import pytest
from app import app, db, Todo
from flask import url_for

# Test package convention: test_todo_app.py
# Use Pytest as the testing framework

class TestTodoApp:
    @pytest.fixture(scope='function')
    def test_client(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.test_client() as testing_client:
            with app.app_context():
                db.create_all()
                yield testing_client
                db.drop_all()

    def test_add_valid_todo_item(self, test_client):
        # Given
        new_todo_data = {'title': 'Buy Groceries'}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Buy Groceries' in response.data
        todo = Todo.query.filter_by(title='Buy Groceries').first()
        assert todo is not None
        assert todo.complete is False

    def test_add_todo_item_with_empty_title(self, test_client):
        # Given
        new_todo_data = {'title': ''}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 400   # Assuming the application returns a 400 Bad Request
        assert b'Error: Title cannot be empty' in response.data

    def test_update_todo_completion_status(self, test_client):
        # Given
        todo = Todo(title='Incomplete Task', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

    def test_delete_todo_item(self, test_client):
        # Given
        todo = Todo(title='Task to Delete', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/delete/{todo.id}', follow_redirects=True)

        # Then
        deleted_todo = Todo.query.filter_by(id=todo.id).first()
        assert deleted_todo is None
        assert response.status_code == 200

    def test_invalid_update_route(self, test_client):
        # Given
        invalid_id = 99999

        # When
        response = test_client.get(f'/update/{invalid_id}', follow_redirects=True)

        # Then
        assert response.status_code == 404   # Assuming the application returns a 404 Not Found
        assert b'Error: Task not found' in response.data

    def test_invalid_delete_route(self, test_client):
        # Given
        invalid_id = 99999

        # When
        response = test_client.get(f'/delete/{invalid_id}', follow_redirects=True)

        # Then
        assert response.status_code == 404   # Assuming the application returns a 404 Not Found
        assert b'Error: Task not found' in response.data

    def test_unique_todo_id_invariant(self, test_client):
        # Given
        todo1 = Todo(title='Task 1', complete=False)
        todo2 = Todo(title='Task 2', complete=False)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # When
        todos = Todo.query.all()

        # Then
        ids = [todo.id for todo in todos]
        assert len(ids) == len(set(ids))  # Ensure all IDs are unique

    def test_task_title_length_limit(self, test_client):
        # Given
        long_title = 'a' * 101
        new_todo_data = {'title': long_title}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 400   # Assuming the application returns a 400 Bad Request
        assert b'Error: Title exceeds maximum length' in response.data

    def test_state_transition_add_new_task(self, test_client):
        # Given
        new_todo_data = {'title': 'Read a Book'}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Read a Book' in response.data
        todo = Todo.query.filter_by(title='Read a Book').first()
        assert todo is not None

        # Cleanup
        test_client.get(f'/delete/{todo.id}', follow_redirects=True)

    def test_state_transition_toggle_task_completion(self, test_client):
        # Given
        todo = Todo(title='Toggle Task', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

        # Toggle back
        test_client.get(f'/update/{todo.id}', follow_redirects=True)
        toggled_todo = Todo.query.filter_by(id=todo.id).first()
        assert toggled_todo.complete is False

    def test_state_transition_delete_task(self, test_client):
        # Given
        todo = Todo(title='Task to Delete Permanently', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/delete/{todo.id}', follow_redirects=True)

        # Then
        deleted_todo = Todo.query.filter_by(id=todo.id).first()
        assert deleted_todo is None
        assert response.status_code == 200

    def test_boundary_task_title_length_min(self, test_client):
        # Given
        new_todo_data = {'title': 'A'}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'A' in response.data
        todo = Todo.query.filter_by(title='A').first()
        assert todo is not None

    def test_boundary_task_title_length_max(self, test_client):
        # Given
        max_title = 'a' * 100
        new_todo_data = {'title': max_title}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert max_title.encode() in response.data
        todo = Todo.query.filter_by(title=max_title).first()
        assert todo is not None

    def test_boundary_task_title_length_empty_string(self, test_client):
        # Given
        new_todo_data = {'title': ''}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Assuming the application returns a 400 Bad Request
        assert b'Error: Title cannot be empty' in response.data

    def test_boundary_task_completion_status_boolean_toggle(self, test_client):
        # Given
        todo = Todo(title='Toggle Completion', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = test_client.get(f'/update/{todo.id}', follow_redirects=True)

        # Then
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True
        assert response.status_code == 200

        # Toggle back
        test_client.get(f'/update/{todo.id}', follow_redirects=True)
        toggled_todo = Todo.query.filter_by(id=todo.id).first()
        assert toggled_todo.complete is False

    def test_security_add_task_sql_injection(self, test_client):
        # Given
        injection_title = 'DROP TABLE Todo;'
        new_todo_data = {'title': injection_title}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code != 500  # Assuming no server error occurs
        assert b'DROP TABLE Todo;' not in response.data
        todo = Todo.query.filter_by(title=injection_title).first()
        assert todo is not None

    def test_security_add_task_xss(self, test_client):
        # Given
        xss_title = '<script>alert("XSS")</script>'
        new_todo_data = {'title': xss_title}

        # When
        response = test_client.post('/add', data=new_todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'<script>' not in response.data
        todo = Todo.query.filter_by(title=xss_title).first()
        assert todo is not None

    def test_cross_entity_task_list_retrieval_consistency(self, test_client):
        # Given
        todo1 = Todo(title='Task 1', complete=False)
        todo2 = Todo(title='Task 2', complete=False)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # When
        response = test_client.get('/', follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data
