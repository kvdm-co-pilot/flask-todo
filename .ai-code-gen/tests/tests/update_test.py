import unittest
from app import app, db, Todo
from flask import url_for
from contextlib import contextmanager

@contextmanager
def app_context():
    with app.app_context():
        yield

@contextmanager
def request_context(path='/'):
    with app.test_request_context(path):
        yield

class UpdateTodoItemTest(unittest.TestCase):
    
    def setUp(self):
        # Given: Set up a temporary database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        # Clean up database after each test
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_update_valid_todo_item(self):
        # Given: A Todo item exists in the database
        todo = Todo(id=5, title="Old Task", description="Incomplete", complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: A valid update is performed
        new_description = 'Complete project documentation'
        with request_context():
            response = self.app.post(url_for('update', todo_id=todo.id), data={'description': new_description}, follow_redirects=True)

        # Then: The database is updated and user is redirected
        with app_context():
            updated_todo = db.session.get(Todo, 5)
        self.assertEqual(updated_todo.description, new_description)
        self.assertEqual(response.status_code, 302)
        with request_context():
            self.assertIn(url_for('home'), response.location)

    def test_update_todo_item_empty_description(self):
        # Given: A Todo item exists in the database
        todo = Todo(id=5, title="Old Task", description="Incomplete", complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: An attempt to update with an empty description is made
        with request_context():
            response = self.app.post(url_for('update', todo_id=todo.id), data={'description': ''}, follow_redirects=True)

        # Then: An error message is displayed and data remains unchanged
        with app_context():
            updated_todo = db.session.get(Todo, 5)
        self.assertEqual(updated_todo.description, "Incomplete")
        self.assertIn(b'Description cannot be empty', response.data)

    def test_update_non_existent_todo_item(self):
        # Given: No Todo item with the specified id exists

        # When: An attempt to update a non-existent Todo is made
        with request_context():
            response = self.app.post(url_for('update', todo_id=999), data={'description': 'New Task'}, follow_redirects=True)

        # Then: A 404 error is returned
        self.assertEqual(response.status_code, 404)

    def test_update_todo_item_max_description_length(self):
        # Given: A Todo item exists in the database
        todo = Todo(id=5, title="Old Task", description="Incomplete", complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: An update with maximum allowed description length is performed
        max_length_description = 'A' * 255
        with request_context():
            response = self.app.post(url_for('update', todo_id=todo.id), data={'description': max_length_description}, follow_redirects=True)

        # Then: The database is updated successfully
        with app_context():
            updated_todo = db.session.get(Todo, 5)
        self.assertEqual(updated_todo.description, max_length_description)
        self.assertEqual(response.status_code, 302)
        with request_context():
            self.assertIn(url_for('home'), response.location)

    def test_update_todo_item_description_exceeding_max_length(self):
        # Given: A Todo item exists in the database
        todo = Todo(id=5, title="Old Task", description="Incomplete", complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: An attempt to update with a description exceeding max length is made
        too_long_description = 'A' * 256
        with request_context():
            response = self.app.post(url_for('update', todo_id=todo.id), data={'description': too_long_description}, follow_redirects=True)

        # Then: An error message is displayed
        self.assertIn(b'Description exceeds maximum length', response.data)

if __name__ == '__main__':
    unittest.main()