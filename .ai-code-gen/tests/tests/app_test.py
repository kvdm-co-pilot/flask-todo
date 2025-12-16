import unittest
from app import app, db, Todo
from flask import url_for
from flask_testing import TestCase

class Functional_AddValidTask_ExpectedSuccess(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_valid_task(self):
        with self.app:
            # Given: A title for a new Todo
            data = {'title': 'Buy groceries'}

            # When: A POST request is made to add the new Todo
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

            # Then: The new Todo should be in the database and home page
            self.assertIn(b'Buy groceries', response.data)
            self.assertEqual(Todo.query.count(), 1)

class Functional_UpdateTaskCompletionStatus_ExpectedToggle(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_update_task_completion_status(self):
        with self.app:
            # Given: A Todo item exists
            todo = Todo(title="Buy groceries", complete=False)
            db.session.add(todo)
            db.session.commit()

            # When: The update endpoint is triggered
            self.app.get(url_for('update', todo_id=todo.id), follow_redirects=True)

            # Then: The Todo's completed status should be toggled
            updated_todo = db.session.get(Todo, todo.id)
            self.assertTrue(updated_todo.complete)

class Functional_DeleteExistingTask_ExpectedRemoval(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_delete_existing_task(self):
        with self.app:
            # Given: A Todo item exists
            todo = Todo(title="Buy groceries", complete=False)
            db.session.add(todo)
            db.session.commit()

            # When: The delete endpoint is triggered
            self.app.get(url_for('delete', todo_id=todo.id), follow_redirects=True)

            # Then: The Todo item should be removed from the database
            self.assertEqual(Todo.query.count(), 0)

class Functional_AddTaskWithoutTitle_ExpectedError(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_task_without_title(self):
        with self.app:
            # Given: An empty title
            data = {'title': ''}

            # When: A POST request is made to add the Todo
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

            # Then: An error message should be displayed
            self.assertIn(b'Title is required', response.data)

if __name__ == '__main__':
    unittest.main()