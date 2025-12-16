import unittest
from app import app, db, Todo
from flask import url_for

class Functional_AddValidTodoTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_valid_todo(self):
        """
        Test adding a valid ToDo item with a specific title.
        Inputs: Form submission with title 'Buy groceries'.
        Expected: New ToDo item titled 'Buy groceries' is saved with complete status 'False'.
        """
        # Given
        initial_count = Todo.query.count()
        # When
        response = self.app.post(url_for('add'), data={'title': 'Buy groceries'})
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            new_count = Todo.query.count()
            self.assertEqual(new_count, initial_count + 1)
            added_todo = Todo.query.filter_by(title='Buy groceries').first()
            self.assertIsNotNone(added_todo)
            self.assertFalse(added_todo.complete)

class Functional_ToggleTodoCompletionStatusTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.todo = Todo(title='Buy groceries', complete=False)
            db.session.add(self.todo)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_toggle_completion_status(self):
        """
        Test toggling the completion status of an existing ToDo item.
        Inputs: Toggle complete status for item with title 'Buy groceries'.
        Expected: Complete status of 'Buy groceries' is updated to 'True'.
        """
        # When
        response = self.app.get(url_for('update', todo_id=self.todo.id))
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            updated_todo = Todo.query.get(self.todo.id)
            self.assertTrue(updated_todo.complete)

class Functional_DeleteExistingTodoTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.todo = Todo(title='Buy groceries', complete=False)
            db.session.add(self.todo)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_delete_existing_todo(self):
        """
        Test deleting an existing ToDo item.
        Inputs: Click delete option for item titled 'Buy groceries'.
        Expected: ToDo item titled 'Buy groceries' is removed from the database.
        """
        # When
        response = self.app.get(url_for('delete', todo_id=self.todo.id))
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            deleted_todo = Todo.query.get(self.todo.id)
            self.assertIsNone(deleted_todo)

if __name__ == "__main__":
    unittest.main()