import unittest
from flask import Flask, request
from your_application import app, db, Todo  # Import the app and models

class AddFunctionalityTest(unittest.TestCase):

    def setUp(self):
        # Given: Setup the test client and test database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_valid_task(self):
        # Given: A valid todo title
        title = 'Buy groceries'

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Check that the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_add_empty_title_task(self):
        # Given: An empty todo title
        title = ''

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title})

        # Then: Check for error message indicating the title cannot be empty
        self.assertIn(b'Title cannot be empty', response.data)

    def test_add_max_character_title_task(self):
        # Given: A todo title of exactly 100 characters
        title = 'A' * 100

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Check that the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_add_special_character_task(self):
        # Given: A todo title with special characters
        title = 'Check emails! 📧📬'

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Check that the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_add_duplicate_title_task(self):
        # Given: A duplicate todo title
        title = 'Buy groceries'

        # Precondition: Add the todo first time
        self.app.post('/add', data={'title': title}, follow_redirects=True)

        # When: Add the duplicate todo
        response = self.app.post('/add', data={'title': title})

        # Then: Check for error message indicating the task already exists
        self.assertIn(b'Task already exists', response.data)

if __name__ == '__main__':
    unittest.main()