import unittest
from app import app, db, Todo
from flask import url_for

class Functional_AddValidTask_Success(unittest.TestCase):
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

    def test_add_valid_task(self):
        with app.app_context():
            initial_count = Todo.query.count()
        response = self.app.post(url_for('add'), data={'title': 'Read a book'})
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            new_count = Todo.query.count()
        self.assertEqual(new_count, initial_count + 1)
        # Verify task display
        response = self.app.get(url_for('home'))
        self.assertIn(b'Read a book', response.data)

class Functional_AddTaskWithoutTitle_ErrorMessage(unittest.TestCase):
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

    def test_add_task_without_title(self):
        response = self.app.post(url_for('add'), data={'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task title is required', response.data)

class Functional_AddTaskWithExcessivelyLongTitle_ErrorMessage(unittest.TestCase):
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

    def test_add_task_with_long_title(self):
        long_title = 'A' * 101
        response = self.app.post(url_for('add'), data={'title': long_title})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task title is too long', response.data)

class Functional_AddTaskWithSpecialCharacters_DisplayCorrectly(unittest.TestCase):
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

    def test_add_task_with_special_characters(self):
        special_title = 'Fix the bug #123! @2pm'
        response = self.app.post(url_for('add'), data={'title': special_title})
        self.assertEqual(response.status_code, 302)  # Redirection
        response = self.app.get(url_for('home'))
        self.assertIn(b'Fix the bug #123! @2pm', response.data)

# Additional tests would follow the same structure...

if __name__ == "__main__":
    unittest.main()