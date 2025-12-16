```python
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

class Functional_TodoItemTest:

    def test_create_todo_item_successfully(self, client):
        # Given
        todo_data = {'title': 'Buy groceries'}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='Buy groceries').first()
        assert todo is not None
        assert todo.title == 'Buy groceries'

    def test_create_todo_item_with_empty_title(self, client):
        # Given
        todo_data = {'title': ''}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert b'Title cannot be empty' in response.data

    def test_update_existing_todo_item(self, client):
        # Setup: create initial todo
        initial_data = {'title': 'Buy groceries'}
        client.post('/todos', json=initial_data)

        # Given
        update_data = {'title': 'Buy groceries and cook dinner'}

        # When
        response = client.put('/todos/1', json=update_data)

        # Then
        assert response.status_code == 200
        todo = Todo.query.get(1)
        assert todo.title == 'Buy groceries and cook dinner'

    def test_delete_todo_item_successfully(self, client):
        # Setup: create initial todo
        initial_data = {'title': 'Buy groceries'}
        client.post('/todos', json=initial_data)

        # When
        response = client.delete('/todos/1')

        # Then
        assert response.status_code == 200
        todo = Todo.query.get(1)
        assert todo is None

    def test_boundary_value_for_title_length(self, client):
        # Given
        todo_data = {'title': 'a'*100}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 201
        todo = Todo.query.filter_by(title='a'*100).first()
        assert todo is not None

    def test_title_length_exceeds_maximum(self, client):
        # Given
        todo_data = {'title': 'a'*101}

        # When
        response = client.post('/todos', json=todo_data)

        # Then
        assert response.status_code == 400
        assert b'Title exceeds maximum length' in response.data

    def test_unique_task_id(self, client):
        # Given
        todo1_data = {'title': 'First task'}
        todo2_data = {'title': 'Second task'}
        client.post('/todos', json=todo1_data)
        client.post('/todos', json=todo2_data)

        # Then
        todo1 = Todo.query.filter_by(title='First task').first()
        todo2 = Todo.query.filter_by(title='Second task').first()
        assert todo1.id != todo2.id

    # Additional tests...
```
