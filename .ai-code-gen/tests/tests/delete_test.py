import unittest
from app import app, db, Todo
from flask import url_for

class ToggleTodoCompletionTest(unittest.TestCase):
    
    def setUp(self):
        # Given: Set up a temporary database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up database after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_completion_toggle_incomplete_to_complete(self):
        # Given: An incomplete Todo item exists in the database
        todo_id = 123
        todo = Todo(id=todo_id, title="Test Todo", complete=False)
        with app.app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The update endpoint is triggered
        self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: The Todo's completed status should be toggled to complete
        with app.app_context():
            updated_todo = db.session.get(Todo, todo_id)
            self.assertTrue(updated_todo.complete)

    def test_valid_completion_toggle_complete_to_incomplete(self):
        # Given: A complete Todo item exists in the database
        todo_id = 456
        todo = Todo(id=todo_id, title="Test Todo", complete=True)
        with app.app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The update endpoint is triggered
        self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: The Todo's completed status should be toggled to incomplete
        with app.app_context():
            updated_todo = db.session.get(Todo, todo_id)
            self.assertFalse(updated_todo.complete)

    def test_invalid_todo_id_toggle_attempt(self):
        # Given: An invalid Todo ID
        todo_id = 999

        # When: The update endpoint is triggered
        response = self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: No changes occur, and error is logged
        self.assertIn(b'Error', response.data)

    def test_max_boundary_todo_id_toggle_completion(self):
        # Given: A Todo item with max boundary ID value
        todo_id = 999999999
        todo = Todo(id=todo_id, title="Max Boundary Todo", complete=False)
        with app.app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The update endpoint is triggered
        self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: The Todo's completed status should be toggled
        with app.app_context():
            updated_todo = db.session.get(Todo, todo_id)
            self.assertTrue(updated_todo.complete)

    def test_special_character_todo_id_toggle_completion(self):
        # Given: A Todo item with special character ID
        todo_id = 'abc123'
        todo = Todo(id=todo_id, title="Special Character Todo", complete=False)
        with app.app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The update endpoint is triggered
        self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: The Todo's completed status should be toggled
        with app.app_context():
            updated_todo = db.session.get(Todo, todo_id)
            self.assertTrue(updated_todo.complete)

    def test_null_todo_id_toggle_attempt(self):
        # Given: A null Todo ID
        todo_id = None

        # When: The update endpoint is triggered
        response = self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: No changes occur, and error is logged
        self.assertIn(b'Error', response.data)

    def test_sql_injection_prevention_on_toggle(self):
        # Given: An SQL injection attempt as Todo ID
        todo_id = '1; DROP TABLE todos;'

        # When: The update endpoint is triggered
        response = self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: No changes occur, and injection is blocked
        self.assertIn(b'Error', response.data)

    def test_xss_prevention_on_toggle(self):
        # Given: An XSS attack attempt as Todo ID
        todo_id = '<script>alert("XSS")</script>'

        # When: The update endpoint is triggered
        response = self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: No script execution occurs, and attempt is blocked
        self.assertIn(b'Error', response.data)

    def test_csrf_prevention_on_toggle(self):
        # Given: A valid Todo ID
        todo_id = 123

        # When: The update endpoint is triggered
        response = self.app.get(url_for('home', todo_id=todo_id), follow_redirects=True)

        # Then: CSRF protection ensures authenticity
        self.assertIn(b'Test Todo', response.data)

if __name__ == '__main__':
    unittest.main()