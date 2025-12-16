import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from your_application import app, db, Todo  # Import the app and models

class CreateTodoTest(unittest.TestCase):

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

    def test_create_todo_with_valid_title(self):
        # Given: A valid todo title
        title = 'Buy groceries'

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Check that the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_create_todo_with_empty_title(self):
        # Given: An empty title
        title = ''

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Ensure error message is displayed
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title cannot be empty', response.data)

    def test_create_todo_with_max_title_length(self):
        # Given: A title with maximum length
        title = 'A' * 100

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Check that the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_create_todo_exceeding_max_title_length(self):
        # Given: A title exceeding maximum length
        title = 'A' * 101

        # When: Add the new todo
        response = self.app.post('/add', data={'title': title}, follow_redirects=True)

        # Then: Ensure error message is displayed
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title is too long', response.data)

    def test_view_todo_items(self):
        # Given: Several todo items exist
        with app.app_context():
            db.session.add(Todo(title='Buy groceries'))
            db.session.add(Todo(title='Complete homework'))
            db.session.commit()

        # When: User views homepage
        response = self.app.get('/', follow_redirects=True)

        # Then: Check that all todo items are displayed
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Buy groceries', response.data)
        self.assertIn(b'Complete homework', response.data)

    def test_delete_todo_item(self):
        # Given: A todo item to delete
        with app.app_context():
            todo = Todo(title='Delete Test')
            db.session.add(todo)
            db.session.commit()

        # When: Delete the todo
        response = self.app.get(f'/delete/{todo.id}', follow_redirects=True)

        # Then: Check that the todo is deleted
        deleted_todo = Todo.query.filter_by(id=todo.id).first()
        self.assertIsNone(deleted_todo)

    def test_update_todo_title(self):
        # Given: A todo item to update
        with app.app_context():
            todo = Todo(title='Old Title')
            db.session.add(todo)
            db.session.commit()

        # When: Update the todo
        new_title = 'Complete homework'
        response = self.app.post(f'/update/{todo.id}', data={'title': new_title}, follow_redirects=True)

        # Then: Check that the todo title is updated
        updated_todo = Todo.query.filter_by(id=todo.id).first()
        self.assertEqual(updated_todo.title, new_title)

if __name__ == '__main__':
    unittest.main()