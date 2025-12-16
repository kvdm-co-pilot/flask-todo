import unittest
from app import app, db, Todo
from flask import url_for

class Functional_CreateNewTodoWithValidTitleTest(unittest.TestCase):
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

    def test_create_new_todo_with_valid_title(self):
        # Given
        title = 'Buy groceries'
        with app.app_context():
            initial_count = Todo.query.count()
        
        # When
        response = self.app.post(url_for('add'), data={'title': title})
        
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            new_count = Todo.query.count()
            self.assertEqual(new_count, initial_count + 1)
            added_todo = Todo.query.filter_by(title=title).first()
            self.assertIsNotNone(added_todo)
            self.assertEqual(added_todo.title, title)


class Functional_CreateTodoWithEmptyTitleTest(unittest.TestCase):
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

    def test_create_todo_with_empty_title(self):
        # Given
        title = ''

        # When
        response = self.app.post(url_for('add'), data={'title': title})

        # Then
        self.assertEqual(response.status_code, 400)  # Bad Request
        self.assertIn(b'Title cannot be empty.', response.data)


class Functional_CreateTodoWithExceedingTitleTest(unittest.TestCase):
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

    def test_create_todo_with_exceeding_title(self):
        # Given
        title = 'This title is intentionally made longer than the 100 character limit to test validation.'

        # When
        response = self.app.post(url_for('add'), data={'title': title})

        # Then
        self.assertEqual(response.status_code, 400)  # Bad Request
        self.assertIn(b'Title cannot exceed 100 characters.', response.data)


if __name__ == "__main__":
    unittest.main()

