# Import statements
import pytest
from app import app, db, Todo
from flask import url_for

# Test package convention: test_<filename>.py
# Use Pytest as the testing framework

class TestTodoApp:
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

    def test_add_todo_item_valid_data(self, test_client):
        # Given
        todo_data = {'title': 'Buy groceries'}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Buy groceries' in response.data
        added_todo = Todo.query.filter_by(title='Buy groceries').first()
        assert added_todo is not None
        assert added_todo.complete is False

    def test_update_todo_item_completion_status(self, test_client):
        # Given
        todo = Todo(title='Sample Task', complete=False)
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
        todo = Todo(title='Task to Delete')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id

        # When
        response = test_client.get(f'/delete/{todo_id}', follow_redirects=True)

        # Then
        deleted_todo = Todo.query.filter_by(id=todo_id).first()
        assert deleted_todo is None
        assert response.status_code == 200

    def test_add_todo_item_empty_title(self, test_client):
        # Given
        todo_data = {'title': ''}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Title cannot be empty' in response.data

    def test_add_todo_item_title_length_limit(self, test_client):
        # Given
        todo_data = {'title': 'A'*101}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Title cannot exceed 100 characters' in response.data

    def test_update_non_existent_todo_item(self, test_client):
        # Given
        non_existent_id = 999

        # When
        response = test_client.get(f'/update/{non_existent_id}', follow_redirects=True)

        # Then
        assert response.status_code == 404
        assert b'Todo item not found' in response.data

    def test_delete_non_existent_todo_item(self, test_client):
        # Given
        non_existent_id = 999

        # When
        response = test_client.get(f'/delete/{non_existent_id}', follow_redirects=True)

        # Then
        assert response.status_code == 404
        assert b'Todo item not found' in response.data

    def test_unique_todo_ids(self, test_client):
        # Given
        todo_data1 = {'title': 'Task 1'}
        todo_data2 = {'title': 'Task 2'}

        # When
        response1 = test_client.post('/add', data=todo_data1, follow_redirects=True)
        response2 = test_client.post('/add', data=todo_data2, follow_redirects=True)

        # Then
        assert response1.status_code == 200
        assert response2.status_code == 200
        todo1 = Todo.query.filter_by(title='Task 1').first()
        todo2 = Todo.query.filter_by(title='Task 2').first()
        assert todo1.id != todo2.id

    def test_task_title_min_length(self, test_client):
        # Given
        todo_data = {'title': 'A'}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'A' in response.data

    def test_task_title_max_length(self, test_client):
        # Given
        todo_data = {'title': 'A'*100}

        # When
        response = test_client.post('/add', data=todo_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'A'*100 in response.data

    def test_task_completion_status_toggle(self, test_client):
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

    def test_task_list_retrieval_consistency(self, test_client):
        # Given
        response = test_client.get('/')

        # When
        todo_list = Todo.query.all()

        # Then
        assert response.status_code == 200
        for todo in todo_list:
            assert bytes(todo.title, 'utf-8') in response.data

    def test_task_visibility_on_ui(self, test_client):
        # Given
        todo_data = {'title': 'UI Task'}
        test_client.post('/add', data=todo_data, follow_redirects=True)

        # When
        response = test_client.get('/')

        # Then
        assert response.status_code == 200
        assert b'UI Task' in response.data
