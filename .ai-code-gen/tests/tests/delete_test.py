import unittest
from app import app, db, Todo
from flask import url_for

class ToggleCompletionStatusTest(unittest.TestCase):
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

    def test_toggle_completion_status_valid_incomplete_to_complete(self):
        # Given
        with app.app_context():
            todo = Todo(title='Incomplete Task', complete=False)
            db.session.add(todo)
            db.session.commit()
        initial_status = todo.complete

        # When
        response = self.app.get(url_for('toggle', todo_id=todo.id))

        # Then
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            updated_todo = Todo.query.get(todo.id)
            self.assertTrue(updated_todo.complete)
            self.assertNotEqual(initial_status, updated_todo.complete)

    def test_toggle_completion_status_valid_complete_to_incomplete(self):
        # Given
        with app.app_context():
            todo = Todo(title='Complete Task', complete=True)
            db.session.add(todo)
            db.session.commit()
        initial_status = todo.complete

        # When
        response = self.app.get(url_for('toggle', todo_id=todo.id))

        # Then
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            updated_todo = Todo.query.get(todo.id)
            self.assertFalse(updated_todo.complete)
            self.assertNotEqual(initial_status, updated_todo.complete)

    def test_toggle_completion_status_non_existent_task_id(self):
        # Given
        non_existent_id = 999

        # When
        response = self.app.get(url_for('toggle', todo_id=non_existent_id))

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Task does not exist', response.data)

    def test_invariant_verification_unique_todo_id(self):
        # Given
        with app.app_context():
            todo1 = Todo(title='Task 1', complete=False)
            todo2 = Todo(title='Task 2', complete=True)
            db.session.add(todo1)
            db.session.add(todo2)
            db.session.commit()
        ids = [todo1.id, todo2.id]

        # Then
        self.assertEqual(len(set(ids)), len(ids))

    def test_boundary_title_length_exceed_limit(self):
        # Given
        long_title = 'A' * 300

        # When
        with app.app_context():
            try:
                todo = Todo(title=long_title, complete=False)
                db.session.add(todo)
                db.session.commit()
            except Exception as e:
                error_message = str(e)

        # Then
        self.assertIn('too long', error_message)

    def test_negative_complete_status_non_boolean_value(self):
        # Given
        invalid_status = 'yes'

        # When
        with app.app_context():
            try:
                todo = Todo(title='Invalid Status Task', complete=invalid_status)
                db.session.add(todo)
                db.session.commit()
            except Exception as e:
                error_message = str(e)

        # Then
        self.assertIn('invalid status value', error_message)

if __name__ == "__main__":
    unittest.main()