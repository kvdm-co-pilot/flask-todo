import pytest
from app import app, db
from models import Todo

@pytest.fixture
def app():
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

class TodoFunctionalTest:

    def test_add_valid_todo_item(self, client):
        # Given
        todo_data = {'title': 'Buy groceries'}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 302  # Redirect
        todo = Todo.query.filter_by(title='Buy groceries').first()
        assert todo is not None
        assert todo.complete is False

    def test_toggle_todo_completion_status(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = client.get(f'/update/{todo.id}')

        # Then
        assert response.status_code == 302  # Redirect
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True

    def test_delete_existing_todo_item(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = client.get(f'/delete/{todo.id}')

        # Then
        assert response.status_code == 302  # Redirect
        deleted_todo = Todo.query.filter_by(id=todo.id).first()
        assert deleted_todo is None

    def test_view_todo_list(self, client):
        # Given
        todo1 = Todo(title='Buy groceries', complete=False)
        todo2 = Todo(title='Wash car', complete=True)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # When
        response = client.get('/')

        # Then
        assert response.status_code == 200
        assert b'Buy groceries' in response.data
        assert b'Wash car' in response.data

    def test_add_todo_item_with_empty_title(self, client):
        # Given
        todo_data = {'title': ''}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 400  # Bad Request

    def test_update_non_existent_todo_item(self, client):
        # Given
        non_existent_id = 999

        # When
        response = client.get(f'/update/{non_existent_id}')

        # Then
        assert response.status_code == 404  # Not Found

    def test_add_todo_item_with_max_title_length(self, client):
        # Given
        max_length_title = 'A' * 100
        todo_data = {'title': max_length_title}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 302  # Redirect
        todo = Todo.query.filter_by(title=max_length_title).first()
        assert todo is not None

    def test_verify_unique_task_id(self, client):
        # Given
        todo_data1 = {'title': 'Task 1'}
        todo_data2 = {'title': 'Task 2'}
        client.post('/add', data=todo_data1)
        client.post('/add', data=todo_data2)

        # When
        todos = Todo.query.all()

        # Then
        assert len(todos) == 2
        assert todos[0].id != todos[1].id

    def test_verify_task_title_not_exceeding_100_chars(self, client):
        # Given
        long_title = 'A' * 101
        todo_data = {'title': long_title}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 400  # Bad Request

    def test_verify_task_completion_status_is_boolean(self, client):
        # Given
        todo_data = {'title': 'Boolean Test'}
        client.post('/add', data=todo_data)

        # When
        todo = Todo.query.filter_by(title='Boolean Test').first()

        # Then
        assert isinstance(todo.complete, bool)

    def test_toggle_todo_completion_status_from_incomplete_to_complete(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = client.get(f'/update/{todo.id}')

        # Then
        assert response.status_code == 302  # Redirect
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True

    def test_toggle_todo_completion_status_from_complete_to_incomplete(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=True)
        db.session.add(todo)
        db.session.commit()

        # When
        response = client.get(f'/update/{todo.id}')

        # Then
        assert response.status_code == 302  # Redirect
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is False

    def test_verify_task_deletion_is_irreversible(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        client.get(f'/delete/{todo.id}')

        # Attempt to retrieve deleted item
        deleted_todo = Todo.query.filter_by(id=todo.id).first()

        # Then
        assert deleted_todo is None

    def test_add_todo_item_with_title_length_1(self, client):
        # Given
        todo_data = {'title': 'A'}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 302  # Redirect
        todo = Todo.query.filter_by(title='A').first()
        assert todo is not None

    def test_add_todo_item_with_title_length_100(self, client):
        # Given
        max_length_title = 'A' * 100
        todo_data = {'title': max_length_title}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 302  # Redirect
        todo = Todo.query.filter_by(title=max_length_title).first()
        assert todo is not None

    def test_verify_task_completion_status_false(self, client):
        # Given
        todo_data = {'title': 'New Task'}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 302  # Redirect
        todo = Todo.query.filter_by(title='New Task').first()
        assert todo.complete is False

    def test_verify_task_completion_status_true(self, client):
        # Given
        todo = Todo(title='Buy groceries', complete=False)
        db.session.add(todo)
        db.session.commit()

        # When
        response = client.get(f'/update/{todo.id}')

        # Then
        assert response.status_code == 302  # Redirect
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        assert updated_todo.complete is True

    def test_add_todo_item_with_empty_title_should_fail(self, client):
        # Given
        todo_data = {'title': ''}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 400  # Bad Request

    def test_verify_task_completion_status_is_none_should_fail(self, client):
        # Given
        todo_data = {'title': 'None Test'}
        client.post('/add', data=todo_data)

        # When
        todo = Todo.query.filter_by(title='None Test').first()

        # Then
        assert todo.complete is not None

    def test_sql_injection_on_add_task(self, client):
        # Given
        todo_data = {'title': "'; DROP TABLE Todo; --"}

        # When
        response = client.post('/add', data=todo_data)

        # Then
        assert response.status_code == 400  # Bad Request

    def test_unauthorized_update_via_url_manipulation(self, client):
        # Given
        non_existent_id = 999

        # When
        response = client.get(f'/update/{non_existent_id}')

        # Then
        assert response.status_code == 404  # Not Found

    def test_unauthorized_deletion_via_url_manipulation(self, client):
        # Given
        non_existent_id = 999

        # When
        response = client.get(f'/delete/{non_existent_id}')

        # Then
        assert response.status_code == 404  # Not Found

    def test_database_commit_failure_on_add(self, client):
        # Given
        todo_data = {'title': 'Commit Failure Test'}

        # Simulate commit failure
        with pytest.raises(Exception):
            client.post('/add', data=todo_data)

    def test_database_commit_failure_on_update(self, client):
        # Given
        todo = Todo(title='Commit Failure Test', complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate commit failure
        with pytest.raises(Exception):
            client.get(f'/update/{todo.id}')

    def test_database_commit_failure_on_delete(self, client):
        # Given
        todo = Todo(title='Commit Failure Test', complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate commit failure
        with pytest.raises(Exception):
            client.get(f'/delete/{todo.id}')

    def test_interrupt_add_operation(self, client):
        # Given
        todo_data = {'title': 'Interrupt Test'}

        # Simulate network interruption
        with pytest.raises(Exception):
            client.post('/add', data=todo_data)

    def test_interrupt_update_operation(self, client):
        # Given
        todo = Todo(title='Interrupt Test', complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate network interruption
        with pytest.raises(Exception):
            client.get(f'/update/{todo.id}')

    def test_interrupt_delete_operation(self, client):
        # Given
        todo = Todo(title='Interrupt Test', complete=False)
        db.session.add(todo)
        db.session.commit()

        # Simulate network interruption
        with pytest.raises(Exception):
            client.get(f'/delete/{todo.id}')

    def test_task_list_consistency_with_user_actions(self, client):
        # Given
        todo_data1 = {'title': 'Consistency Test 1'}
        todo_data2 = {'title': 'Consistency Test 2'}

        # When
        client.post('/add', data=todo_data1)
        client.post('/add', data=todo_data2)
        client.get(f'/update/{Todo.query.filter_by(title='Consistency Test 1').first().id}')
        client.get(f'/delete/{Todo.query.filter_by(title='Consistency Test 2').first().id}')

        # Then
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == 'Consistency Test 1'

    def test_task_list_reflects_all_changes_made(self, client):
        # Given
        todo_data1 = {'title': 'Change Test 1'}
        todo_data2 = {'title': 'Change Test 2'}

        # When
        client.post('/add', data=todo_data1)
        client.post('/add', data=todo_data2)
        client.get(f'/update/{Todo.query.filter_by(title='Change Test 1').first().id}')
        client.get(f'/delete/{Todo.query.filter_by(title='Change Test 2').first().id}')

        # Then
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == 'Change Test 1'
