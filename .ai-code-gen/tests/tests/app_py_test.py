import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from your_application import app, db, Todo  # Import the app and models

class TodoFunctionalTest(unittest.TestCase):

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

    def test_add_todo_with_valid_title(self):
        # Given: A valid todo title
        valid_title = 'Buy groceries'

        # When: Adding the new todo
        response = self.app.post('/add', data={'title': valid_title}, follow_redirects=True)

        # Then: Verify the todo is added as incomplete
        self.assertIn(valid_title.encode(), response.data)
        self.assertIn(b'Buy groceries', response.data)

    def test_update_todo_completion_status(self):
        # Given: Add a new todo to update
        with app.app_context():
            new_todo = Todo(title='Read a book', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Update the todo completion status
        response = self.app.get(f'/update/{new_todo.id}', follow_redirects=True)

        # Then: Verify the todo is marked as complete
        updated_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertTrue(updated_todo.complete)

    def test_delete_todo_successfully(self):
        # Given: Add a new todo to delete
        with app.app_context():
            new_todo = Todo(title='Wash dishes', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Delete the todo
        response = self.app.get(f'/delete/{new_todo.id}', follow_redirects=True)

        # Then: Verify the todo is removed
        deleted_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertIsNone(deleted_todo)

    def test_add_todo_with_empty_title(self):
        # Given: An empty todo title
        empty_title = ''

        # When: Attempting to add the empty title
        response = self.app.post('/add', data={'title': empty_title}, follow_redirects=True)

        # Then: Verify the error message
        self.assertIn(b'Title cannot be empty', response.data)

    def test_update_non_existent_todo(self):
        # Given: A non-existent todo ID
        non_existent_id = 999

        # When: Attempting to update the non-existent todo
        response = self.app.get(f'/update/{non_existent_id}', follow_redirects=True)

        # Then: Verify the error message
        self.assertIn(b'Item not found', response.data)

    def test_delete_non_existent_todo(self):
        # Given: A non-existent todo ID
        non_existent_id = 999

        # When: Attempting to delete the non-existent todo
        response = self.app.get(f'/delete/{non_existent_id}', follow_redirects=True)

        # Then: Verify the error message
        self.assertIn(b'Item not found', response.data)

if __name__ == '__main__':
    unittest.main()