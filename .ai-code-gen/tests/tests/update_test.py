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

class TestTodoFunctionality:
    def test_add_valid_todo_item(self, client):
        # Given
        todo_data = {'title': 'Buy Groceries', 'description': 'Milk, Eggs, Bread', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='Buy Groceries').first()
        assert todo is not None
        assert todo.description == 'Milk, Eggs, Bread'

    def test_update_todo_item_with_valid_id(self, client):
        # Given
        initial_data = {'title': 'Buy Groceries', 'description': 'Milk, Eggs, Bread', 'user_id': 12345}
        client.post('/todos', json=initial_data)

        update_data = {'title': 'Buy Groceries and Vegetables'}

        # When
        response = client.put('/todos/1001', json=update_data)

        # Then
        assert response.status_code == 200
        updated_todo = Todo.query.get(1001)
        assert updated_todo.title == 'Buy Groceries and Vegetables'

    def test_view_todo_list_after_adding_item(self, client):
        # Given
        todo_data = {'title': 'Buy Groceries', 'description': 'Milk, Eggs, Bread', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.get('/todos')

        # Then
        assert response.status_code == 200
        todos = response.get_json()
        assert any(todo['title'] == 'Buy Groceries' for todo in todos)

    def test_attempt_update_todo_with_invalid_id(self, client):
        # Given
        update_data = {'title': 'Non-existent Item'}

        # When
        response = client.put('/todos/9999', json=update_data)

        # Then
        assert response.status_code == 404
        assert "item cannot be found" in response.get_json()['message']

    def test_add_todo_item_with_missing_details(self, client):
        # Given
        todo_data = {'title': '', 'description': '', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert "missing information" in response.get_json()['message']

    def test_add_todo_item_with_max_length_title(self, client):
        # Given
        todo_data = {'title': 'A'*255, 'description': 'Long title test', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='A'*255).first()
        assert todo is not None

    def test_update_todo_item_with_max_length_title(self, client):
        # Given
        initial_data = {'title': 'Short Title', 'description': 'Short description', 'user_id': 12345}
        client.post('/todos', json=initial_data)

        update_data = {'title': 'A'*255}

        # When
        response = client.put('/todos/1001', json=update_data)

        # Then
        assert response.status_code == 200
        updated_todo = Todo.query.get(1001)
        assert updated_todo.title == 'A'*255

    def test_verify_unique_task_id(self, client):
        # Given
        todo_data1 = {'title': 'Task 1', 'description': 'Description 1', 'user_id': 12345}
        todo_data2 = {'title': 'Task 2', 'description': 'Description 2', 'user_id': 12345}
        client.post('/todos', json=todo_data1)
        client.post('/todos', json=todo_data2)

        # When
        todo1 = Todo.query.filter_by(title='Task 1').first()
        todo2 = Todo.query.filter_by(title='Task 2').first()

        # Then
        assert todo1.id != todo2.id

    def test_verify_task_title_max_length(self, client):
        # Given
        todo_data = {'title': 'A'*256, 'description': 'Exceeds max length', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert "title length exceeds limit" in response.get_json()['message']

    def test_verify_task_completion_status_boolean(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        client.put('/todos/1001/complete')
        completed_todo = Todo.query.get(1001)

        # Then
        assert isinstance(completed_todo.completed, bool)

    def test_task_marked_complete(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        client.put('/todos/1001/complete')

        # Then
        completed_todo = Todo.query.get(1001)
        assert completed_todo.completed is True

    def test_task_deletion(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.delete('/todos/1001')

        # Then
        assert response.status_code == 200
        deleted_todo = Todo.query.get(1001)
        assert deleted_todo is None

    def test_handle_database_commit_failure_during_completion(self, client, app):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # Simulate failure
        with app.app_context():
            db.session.rollback()

        # When
        response = client.put('/todos/1001/complete')

        # Then
        assert response.status_code == 500
        assert "database issue" in response.get_json()['message']

    def test_handle_database_commit_failure_during_deletion(self, client, app):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # Simulate failure
        with app.app_context():
            db.session.rollback()

        # When
        response = client.delete('/todos/1001')

        # Then
        assert response.status_code == 500
        assert "database issue" in response.get_json()['message']

    def test_boundary_verify_task_title_length_min(self, client):
        # Given
        todo_data = {'title': 'A', 'description': 'Minimum length test', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='A').first()
        assert todo is not None

    def test_boundary_verify_task_title_length_max(self, client):
        # Given
        todo_data = {'title': 'A'*255, 'description': 'Maximum length test', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='A'*255).first()
        assert todo is not None

    def test_boundary_verify_task_title_length_empty_string(self, client):
        # Given
        todo_data = {'title': '', 'description': 'Empty title test', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert "missing title" in response.get_json()['message']

    def test_boundary_verify_task_completion_status_min_false(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        client.put('/todos/1001', json={'completed': False})

        # Then
        completed_todo = Todo.query.get(1001)
        assert completed_todo.completed is False

    def test_boundary_verify_task_completion_status_max_true(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        client.put('/todos/1001', json={'completed': True})

        # Then
        completed_todo = Todo.query.get(1001)
        assert completed_todo.completed is True

    def test_boundary_verify_task_completion_status_none_value(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.put('/todos/1001', json={'completed': None})

        # Then
        assert response.status_code == 400
        assert "invalid status value" in response.get_json()['message']

    def test_security_injection_attacks_on_add_task(self, client):
        # Given
        todo_data = {'title': "'); DROP TABLE todos;--", 'description': 'Injection test', 'user_id': 12345}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert "sanitizes input" in response.get_json()['message']

    def test_security_unauthorized_status_change_via_url_manipulation(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.put('/todos/1001/change_status')

        # Then
        assert response.status_code == 403
        assert "prevents unauthorized status changes" in response.get_json()['message']

    def test_security_unauthorized_deletion_via_url_manipulation(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.delete('/todos/1001')

        # Then
        assert response.status_code == 403
        assert "prevents unauthorized deletions" in response.get_json()['message']

    def test_failure_handle_database_connection_failure_on_add(self, client, app):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}

        # Simulate failure
        with app.app_context():
            db.session.rollback()

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 500
        assert "database issue" in response.get_json()['message']

    def test_failure_handle_database_connection_failure_on_update(self, client, app):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # Simulate failure
        with app.app_context():
            db.session.rollback()

        # When
        response = client.put('/todos/1001', json={'title': 'Updated Task'})

        # Then
        assert response.status_code == 500
        assert "database issue" in response.get_json()['message']

    def test_recovery_verify_app_recovery_after_database_connection_restoration(self, client, app):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}

        # Simulate failure
        with app.app_context():
            db.session.rollback()

        # Restore connection
        with app.app_context():
            db.session.commit()

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        assert "resumes normal operations" in response.get_json()['message']

    def test_cross_entity_verify_task_list_consistency_after_add(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.get('/todos')

        # Then
        assert response.status_code == 200
        todos = response.get_json()
        assert any(todo['title'] == 'Task' for todo in todos)

    def test_cross_entity_verify_task_list_consistency_after_update(self, client):
        # Given
        initial_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=initial_data)

        update_data = {'title': 'Updated Task'}
        client.put('/todos/1001', json=update_data)

        # When
        response = client.get('/todos')

        # Then
        assert response.status_code == 200
        todos = response.get_json()
        assert any(todo['title'] == 'Updated Task' for todo in todos)

    def test_cross_entity_verify_task_list_consistency_after_deletion(self, client):
        # Given
        todo_data = {'title': 'Task', 'description': 'Complete this task', 'user_id': 12345}
        client.post('/todos', json=todo_data)

        # When
        response = client.delete('/todos/1001')

        # Then
        assert response.status_code == 200
        response = client.get('/todos')
        todos = response.get_json()
        assert all(todo['title'] != 'Task' for todo in todos)

