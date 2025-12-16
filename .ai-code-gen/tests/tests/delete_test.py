from app import app, db, Todo
import pytest
from werkzeug.exceptions import NotFound
from flask import redirect, url_for

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()


class TodoToggleCompletionStatusTest:
    def test_toggle_completion_valid_todo_item(self, test_client):
        # Given: A todo item with id '123' and complete status False
        todo = Todo(id='123', title="Sample Task", complete=False)
        db.session.add(todo)
        db.session.commit()

        # When: Toggling the completion status
        response = test_client.post('/toggle', data=dict(todo_id='123'), follow_redirects=True)

        # Then: Verify the completion status is True and database update
        updated_todo = Todo.query.filter_by(id='123').first()
        assert response.status_code == 200
        assert updated_todo.complete is True

    def test_toggle_completion_already_completed_todo_item(self, test_client):
        # Given: A todo item with id '456' and complete status True
        todo = Todo(id='456', title="Completed Task", complete=True)
        db.session.add(todo)
        db.session.commit()

        # When: Toggling the completion status
        response = test_client.post('/toggle', data=dict(todo_id='456'), follow_redirects=True)

        # Then: Verify the completion status is False and database update
        updated_todo = Todo.query.filter_by(id='456').first()
        assert response.status_code == 200
        assert updated_todo.complete is False

    def test_toggle_completion_non_existing_todo_item(self, test_client):
        # Given: No todo item with id '789' in database

        # When: Attempt to toggle completion status
        with pytest.raises(NotFound) as exc_info:
            test_client.post('/toggle', data=dict(todo_id='789'))

        # Then: Verify error raised with no database change
        assert "not found" in str(exc_info.value)

    def test_toggle_completion_first_todo_item_in_list(self, test_client):
        # Given: The first todo item with id '1' and complete status False
        todo = Todo(id='1', title="First Task", complete=False)
        db.session.add(todo)
        db.session.commit()

        # When: Toggling the completion status
        response = test_client.post('/toggle', data=dict(todo_id='1'), follow_redirects=True)

        # Then: Verify completion status is True and database update
        updated_todo = Todo.query.filter_by(id='1').first()
        assert response.status_code == 200
        assert updated_todo.complete is True

    def test_toggle_completion_last_todo_item_in_large_list(self, test_client):
        # Given: The last todo item with id '99999' and complete status True
        todo = Todo(id='99999', title="Last Task", complete=True)
        db.session.add(todo)
        db.session.commit()

        # When: Toggling the completion status
        response = test_client.post('/toggle', data=dict(todo_id='99999'), follow_redirects=True)

        # Then: Verify completion status is False and database update
        updated_todo = Todo.query.filter_by(id='99999').first()
        assert response.status_code == 200
        assert updated_todo.complete is False