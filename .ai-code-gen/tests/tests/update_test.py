import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from your_application import app, db, Todo  # Import the app and models

class Functional_ValidNewTodoAdditionTest(unittest.TestCase):

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

    def test_valid_new_todo_addition(self):
        # Given: A valid todo item
        title = 'Buy groceries'
        description = 'Buy milk, eggs, and bread'

        # When: Add the new todo item
        response = self.app.post('/add', data={'title': title, 'description': description}, follow_redirects=True)

        # Then: Check that the todo is added and user is redirected
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)
        self.assertIn(description.encode(), response.data)

class Functional_ValidTodoUpdateTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Add initial todo
            self.todo = Todo(title='Buy groceries', complete=False)
            db.session.add(self.todo)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_todo_update(self):
        # Given: An existing todo item
        new_title = 'Buy groceries and vegetables'

        # When: Update the todo item
        response = self.app.post(f'/update/{self.todo.id}', data={'title': new_title}, follow_redirects=True)

        # Then: Check the todo is updated
        updated_todo = Todo.query.filter_by(id=self.todo.id).first()
        self.assertEqual(updated_todo.title, new_title)

class Functional_EmptyTodoSubmissionTest(unittest.TestCase):

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

    def test_empty_todo_submission(self):
        # Given: An empty todo item
        title = ''
        description = ''

        # When: Add the empty todo item
        response = self.app.post('/add', data={'title': title, 'description': description}, follow_redirects=True)

        # Then: Check that error message is shown and item is not added
        self.assertEqual(response.status_code, 400)  # Assuming 400 for bad request
        self.assertIn(b'Error: Title cannot be empty', response.data)  # Error message expected

if __name__ == '__main__':
    unittest.main()