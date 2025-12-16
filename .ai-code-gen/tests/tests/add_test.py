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

class AddTodoItemTest:
    def test_add_valid_todo_item(self, client):
        # Given
        title = 'Buy groceries'
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 200
        assert title in response.get_data(as_text=True)

    def test_add_empty_title_todo_item(self, client):
        # Given
        title = ''
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 400
        assert 'Title cannot be empty' in response.get_data(as_text=True)

    def test_add_long_title_todo_item(self, client):
        # Given
        title = 'A' * 101
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 400
        assert 'Title is too long' in response.get_data(as_text=True)

    def test_add_special_characters_todo_item(self, client):
        # Given
        title = '@#$%^&*()'
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 200
        assert title in response.get_data(as_text=True)

    def test_add_multiple_todo_items(self, client):
        # Given
        titles = ['Buy groceries', 'Call mom', 'Read a book']
        data = [{'title': title} for title in titles]

        # When
        responses = [client.post('/add', data=d) for d in data]

        # Then
        for response, title in zip(responses, titles):
            assert response.status_code == 200
            assert title in response.get_data(as_text=True)

    def test_unique_task_id(self, client):
        # Given
        title = 'Buy groceries'
        data = {'title': title}

        # When
        response1 = client.post('/add', data=data)
        response2 = client.post('/add', data=data)

        # Then
        assert response1.status_code == 200
        assert response2.status_code == 200
        todo1 = Todo.query.filter_by(title=title).first()
        todo2 = Todo.query.filter_by(title=title).order_by(Todo.id.desc()).first()
        assert todo1.id != todo2.id

    def test_task_title_max_length(self, client):
        # Given
        title = 'A' * 100
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 200
        assert title in response.get_data(as_text=True)

    def test_task_completion_status_boolean(self):
        # Given
        task = Todo(title='Sample task', completed=False)
        db.session.add(task)
        db.session.commit()

        # Then
        assert isinstance(task.completed, bool)

    def test_mark_task_complete(self, client):
        # Given
        task = Todo(title='Sample task', completed=False)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # When
        response = client.post(f'/complete_task/{task_id}')

        # Then
        assert response.status_code == 200
        task = Todo.query.get(task_id)
        assert task.completed is True

    def test_delete_task(self, client):
        # Given
        task = Todo(title='Sample task')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # When
        response = client.post(f'/delete_task/{task_id}')

        # Then
        assert response.status_code == 200
        task = Todo.query.get(task_id)
        assert task is None

    def test_task_title_min_length(self, client):
        # Given
        title = 'A'
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 200
        assert title in response.get_data(as_text=True)

    def test_task_title_max_length_boundary(self, client):
        # Given
        title = 'A' * 100
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 200
        assert title in response.get_data(as_text=True)

    def test_task_title_empty_string(self, client):
        # Given
        title = ''
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 400
        assert 'Title cannot be empty' in response.get_data(as_text=True)

    def test_task_completion_status_none(self):
        # Given
        task = Todo(title='Sample task', completed=None)
        db.session.add(task)
        db.session.commit()

        # Then
        assert task.completed is not None

    def test_add_task_injection_attack(self, client):
        # Given
        title = "'; DROP TABLE todos; --"
        data = {'title': title}

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 400
        assert 'Invalid input' in response.get_data(as_text=True)

    def test_update_task_status_unauthorized_change(self, client):
        # Given
        url = '/update_status?task_id=123&status=true'

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 403

    def test_delete_task_unauthorized_access(self, client):
        # Given
        url = '/delete_task?task_id=123'

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 403

    def test_database_commit_failure_on_add(self, client, monkeypatch):
        # Given
        title = 'Buy groceries'
        data = {'title': title}

        def mock_commit():
            raise Exception('Database commit failed')

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        # When
        response = client.post('/add', data=data)

        # Then
        assert response.status_code == 500
        assert 'Database commit failed' in response.get_data(as_text=True)

    def test_database_commit_failure_on_complete(self, client, monkeypatch):
        # Given
        task = Todo(title='Sample task', completed=False)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        def mock_commit():
            raise Exception('Database commit failed')

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        # When
        response = client.post(f'/complete_task/{task_id}')

        # Then
        assert response.status_code == 500
        assert 'Database commit failed' in response.get_data(as_text=True)

    def test_database_commit_failure_on_delete(self, client, monkeypatch):
        # Given
        task = Todo(title='Sample task')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        def mock_commit():
            raise Exception('Database commit failed')

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        # When
        response = client.post(f'/delete_task/{task_id}')

        # Then
        assert response.status_code == 500
        assert 'Database commit failed' in response.get_data(as_text=True)

    def test_consistency_task_list_after_add(self, client):
        # Given
        titles = ['Buy groceries', 'Call mom', 'Read a book']
        data = [{'title': title} for title in titles]

        # When
        for d in data:
            client.post('/add', data=d)

        # Then
        response = client.get('/todos')
        assert response.status_code == 200
        todos = response.get_json()
        assert len(todos) == len(titles)
        assert all(todo['title'] in titles for todo in todos)

    def test_consistency_task_list_after_complete(self, client):
        # Given
        task = Todo(title='Sample task', completed=False)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # When
        client.post(f'/complete_task/{task_id}')

        # Then
        response = client.get('/todos')
        assert response.status_code == 200
        todos = response.get_json()
        assert any(todo['completed'] is True for todo in todos)

    def test_consistency_task_list_after_delete(self, client):
        # Given
        task = Todo(title='Sample task')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # When
        client.post(f'/delete_task/{task_id}')

        # Then
        response = client.get('/todos')
        assert response.status_code == 200
        todos = response.get_json()
        assert not any(todo['id'] == task_id for todo in todos)
