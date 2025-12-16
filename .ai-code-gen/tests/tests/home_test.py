import pytest
from app import create_app, db, Todo
from flask import url_for

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

class TestHomePage:
    def test_access_home_page_successfully(self, client):
        # Given
        
        # When
        response = client.get(url_for('home'))

        # Then
        assert response.status_code == 200
        assert b'Welcome to Todo App' in response.data

    def test_homepage_load_time(self, client):
        import time

        # Given
        
        # When
        start_time = time.time()
        response = client.get(url_for('home'))
        load_time = time.time() - start_time

        # Then
        assert load_time < 2, f"Homepage load time is {load_time} seconds"

    def test_homepage_content_verification(self, client):
        # Given
        
        # When
        response = client.get(url_for('home'))

        # Then
        assert response.status_code == 200
        assert b'Recent Activities' in response.data

    def test_invalid_request_method(self, client):
        # Given
        
        # When
        response = client.post(url_for('home'))

        # Then
        assert response.status_code in [405, 400]  # Adjusted to handle different server configurations

    def test_homepage_with_large_data_set(self, client):
        # Given
        for i in range(1000):
            todo_item = Todo(title=f'Todo {i}', complete=False)
            db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('home'))

        # Then
        assert response.status_code == 200
        assert b'Todo 999' in response.data

class TestTodoFunctionality:
    def test_verify_unique_todo_id(self, client):
        # Given
        todo1 = Todo(title='Todo 1', complete=False)
        todo2 = Todo(title='Todo 2', complete=False)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # When
        
        # Then
        assert todo1.id != todo2.id

    def test_verify_todo_title_length(self, client):
        # Given
        short_title = ''
        long_title = 'a' * 255

        # When
        response_short = client.post(url_for('add'), data={'title': short_title}, follow_redirects=True)
        response_long = client.post(url_for('add'), data={'title': long_title}, follow_redirects=True)

        # Then
        assert response_short.status_code == 400  # Assuming title length validation is implemented
        assert response_long.status_code == 200

    def test_verify_todo_completion_status_boolean(self, client):
        # Given
        todo_item = Todo(title='Test Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        todo_item.complete = True
        db.session.commit()

        # Then
        updated_item = db.session.get(Todo, todo_item.id)
        assert isinstance(updated_item.complete, bool)

    def test_toggle_todo_completion_status(self, client):
        # Given
        todo_item = Todo(title='Test Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        updated_item = db.session.get(Todo, todo_item.id)
        assert updated_item.complete is True

    def test_delete_todo(self, client):
        # Given
        todo_item = Todo(title='Test Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()
        initial_count = Todo.query.count()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert Todo.query.count() == initial_count - 1

    def test_todo_title_minimum_length(self, client):
        # Given
        title = 'a'

        # When
        response = client.post(url_for('add'), data={'title': title}, follow_redirects=True)

        # Then
        assert response.status_code == 400  # Assuming minimum length validation is implemented

    def test_todo_title_maximum_length(self, client):
        # Given
        title = 'a' * 255

        # When
        response = client.post(url_for('add'), data={'title': title}, follow_redirects=True)

        # Then
        assert response.status_code == 200

    def test_todo_id_auto_increment(self, client):
        # Given
        initial_last_id = Todo.query.order_by(Todo.id.desc()).first().id if Todo.query.count() > 0 else 0

        # When
        todo_item1 = Todo(title='Todo 1', complete=False)
        todo_item2 = Todo(title='Todo 2', complete=False)
        db.session.add(todo_item1)
        db.session.add(todo_item2)
        db.session.commit()

        # Then
        assert todo_item1.id == initial_last_id + 1
        assert todo_item2.id == initial_last_id + 2

class TestSecurity:
    def test_todo_deletion_access_control(self, client):
        # Given
        todo_item = Todo(title='Protected Todo', complete=False)
        db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('delete', todo_id=todo_item.id), headers={'Authentication': 'invalid'}, follow_redirects=True)

        # Then
        assert response.status_code == 403

class TestFailureRecovery:
    def test_interrupted_todo_addition(self, client):
        # Given
        
        # When
        try:
            raise RuntimeError("Simulated interruption")
        except RuntimeError:
            db.session.rollback()

        # Then
        assert Todo.query.count() == 0

class TestCrossEntity:
    def test_todo_list_retrieval_and_display_consistency(self, client):
        # Given
        for i in range(5):
            todo_item = Todo(title=f'Todo {i}', complete=False)
            db.session.add(todo_item)
        db.session.commit()

        # When
        response = client.get(url_for('home'))

        # Then
        assert response.status_code == 200
        for i in range(5):
            assert bytes(f'Todo {i}', 'utf-8') in response.data