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

class TestTodo:
    """
    Test class for managing Todo items.
    """

    def test_add_todo_with_valid_title(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': 'Grocery Shopping'}

        # When
        response = client.post(url_for('add_todo'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).count() == initial_count + 1
        added_item = db.session.query(Todo).filter_by(title='Grocery Shopping').first()
        assert added_item is not None
        assert added_item.title == 'Grocery Shopping'

    def test_view_all_todos(self, client):
        # Given
        db.session.add(Todo(title='Complete Assignment'))
        db.session.add(Todo(title='Buy Milk'))
        db.session.commit()

        # When
        response = client.get(url_for('view_all_todos'))

        # Then
        assert response.status_code == 200
        assert b'Complete Assignment' in response.data
        assert b'Buy Milk' in response.data

    def test_edit_todo_title_successfully(self, client):
        # Given
        todo_item = Todo(title='Complete Assignment')
        db.session.add(todo_item)
        db.session.commit()

        # When
        data = {'title': 'Complete Math Assignment'}
        response = client.post(url_for('edit_todo', todo_id=todo_item.id), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.title == 'Complete Math Assignment'

    def test_delete_todo_successfully(self, client):
        # Given
        todo_item = Todo(title='Buy Milk')
        db.session.add(todo_item)
        db.session.commit()
        initial_count = db.session.query(Todo).count()

        # When
        response = client.get(url_for('delete_todo', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert db.session.query(Todo).count() == initial_count - 1

    def test_add_todo_with_empty_title(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': ''}

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 400  # Assuming 400 for validation error
        assert b'Title cannot be empty' in response.data
        assert db.session.query(Todo).count() == initial_count

    def test_add_todo_with_max_title_length(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        max_title = 'A' * 100
        data = {'title': max_title}

        # When
        response = client.post(url_for('add_todo'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        item = db.session.query(Todo).filter_by(title=max_title).first()
        assert item is not None
        assert item.title == max_title

    def test_add_todo_exceeding_max_title_length(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': 'A' * 101}

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 400  # Assuming 400 for validation error
        assert b'Title exceeds maximum length' in response.data
        assert db.session.query(Todo).count() == initial_count

    def test_verify_unique_todo_id(self, client):
        # Given
        data1 = {'title': 'Task A'}
        data2 = {'title': 'Task B'}

        # When
        response1 = client.post(url_for('add_todo'), data=data1, follow_redirects=True)
        response2 = client.post(url_for('add_todo'), data=data2, follow_redirects=True)

        # Then
        assert response1.status_code == 200
        assert response2.status_code == 200
        item1 = db.session.query(Todo).filter_by(title='Task A').first()
        item2 = db.session.query(Todo).filter_by(title='Task B').first()
        assert item1.id != item2.id

    def test_verify_todo_title_max_length(self, client):
        # Given
        data = {'title': 'A' * 101}

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 400  # Assuming 400 for validation error
        assert b'Title exceeds maximum length' in response.data

    def test_verify_todo_completion_status_boolean(self, client):
        # Given
        todo_item = Todo(title='Task A', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update_todo', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is True

    def test_change_todo_completion_status(self, client):
        # Given
        todo_item = Todo(title='Task A', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update_todo', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is True

    def test_delete_todo_irreversibly(self, client):
        # Given
        todo_item = Todo(title='Task A')
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('delete_todo', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        deleted_item = db.session.get(Todo, todo_item.id)
        assert deleted_item is None

    def test_boundary_todo_title_min_length(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': ''}

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 400  # Assuming 400 for validation error
        assert b'Title cannot be empty' in response.data
        assert db.session.query(Todo).count() == initial_count

    def test_boundary_todo_title_max_length(self, client):
        # Given
        max_title = 'A' * 100
        initial_count = db.session.query(Todo).count()
        data = {'title': max_title}

        # When
        response = client.post(url_for('add_todo'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        added_item = db.session.query(Todo).filter_by(title=max_title).first()
        assert added_item is not None
        assert added_item.title == max_title

    def test_boundary_todo_id_positive_integer(self, client):
        # Given
        data = {'title': 'Task A'}

        # When
        response = client.post(url_for('add_todo'), data=data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        added_item = db.session.query(Todo).filter_by(title='Task A').first()
        assert added_item is not None
        assert added_item.id > 0

    def test_boundary_todo_completion_status_boolean(self, client):
        # Given
        todo_item = Todo(title='Task A', complete=True)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('view_all_todos'))

        # Then
        assert response.status_code == 200
        assert b'Task A' in response.data

    def test_security_sql_injection_on_todo_addition(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': "Task A'; DROP TABLE Todos; --"}

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 400  # Assuming 400 for validation error
        assert b'SQL injection attempt detected' in response.data
        assert db.session.query(Todo).count() == initial_count

    def test_security_unauthorized_access_on_todo_deletion(self, client):
        # Given
        todo_item = Todo(title='Task A')
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('delete_todo', todo_id=todo_item.id))

        # Then
        assert response.status_code == 403  # Assuming 403 for unauthorized access
        assert b'Unauthorized access' in response.data

    def test_failure_recovery_database_connection_loss_during_todo_addition(self, client):
        # Given
        initial_count = db.session.query(Todo).count()
        data = {'title': 'Task A'}

        # Simulate database outage
        db.session.remove()

        # When
        response = client.post(url_for('add_todo'), data=data)

        # Then
        assert response.status_code == 500  # Assuming 500 for server error
        assert b'Database connection lost' in response.data
        assert db.session.query(Todo).count() == initial_count

    def test_failure_recovery_interruption_during_todo_deletion(self, client):
        # Given
        todo_item = Todo(title='Task A')
        db.session.add(todo_item)
        db.session.commit()

        # Simulate interruption
        db.session.remove()

        # When
        response = client.get(url_for('delete_todo', todo_id=todo_item.id))

        # Then
        assert response.status_code == 500  # Assuming 500 for server error
        assert b'Deletion interrupted' in response.data
        assert db.session.get(Todo, todo_item.id) is not None

    def test_consistency_verify_all_todos_retrieved_correctly(self, client):
        # Given
        db.session.add(Todo(title='Task A'))
        db.session.add(Todo(title='Task B'))
        db.session.commit()

        # When
        response = client.get(url_for('view_all_todos'))

        # Then
        assert response.status_code == 200
        assert b'Task A' in response.data
        assert b'Task B' in response.data