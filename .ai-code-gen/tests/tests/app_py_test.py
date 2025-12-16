import unittest
from app import app, db, Todo
from flask import url_for

class Functional_AddNewTodoItemWithValidTitleTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_new_todo_item_with_valid_title(self):
        # Given: A valid title for a new Todo item
        data = {'title': 'Complete the assignment'}

        # When: A POST request is made to add the new Todo item
        response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo item should be in the database and home page
        self.assertIn(b'Complete the assignment', response.data)
        self.assertEqual(Todo.query.count(), 1)

class Functional_UpdateTodoItemStatusTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Given: A Todo item exists in the database
        self.todo = Todo(title="Test Todo", complete=False)
        db.session.add(self.todo)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_update_todo_item_status(self):
        # When: The update endpoint is triggered
        self.app.get(url_for('update', todo_id=self.todo.id), follow_redirects=True)

        # Then: The Todo's completed status should be toggled
        updated_todo = db.session.get(Todo, self.todo.id)
        self.assertTrue(updated_todo.complete)

class Functional_DeleteExistingTodoItemTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Given: A Todo item exists in the database
        self.todo = Todo(title="Test Todo", complete=False)
        db.session.add(self.todo)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_delete_existing_todo_item(self):
        # When: The delete endpoint is triggered
        self.app.get(url_for('delete', todo_id=self.todo.id), follow_redirects=True)

        # Then: The Todo item should be removed from the database
        self.assertEqual(Todo.query.count(), 0)

class Negative_AddTodoItemWithEmptyTitleTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_todo_item_with_empty_title(self):
        # Given: An empty title for a new Todo item
        data = {'title': ''}

        # When: A POST request is made to add the new Todo item
        response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The application should not add a new todo item
        self.assertEqual(Todo.query.count(), 0)
        self.assertIn(b'Error message', response.data)  # Replace with actual error message

class Boundary_AddTodoItemWithMaxTitleLengthTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_todo_item_with_max_title_length(self):
        # Given: A title with maximum allowed length
        data = {'title': 'x' * 100}

        # When: A POST request is made to add the new Todo item
        response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo item should be in the database
        self.assertIn(b'x' * 100, response.data)
        self.assertEqual(Todo.query.count(), 1)

class Exact_ViewEmptyTodoListTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_view_empty_todo_list(self):
        # When: The home page is requested with no items in the database
        response = self.app.get(url_for('home'))

        # Then: A message indicating the todo list is empty should be displayed
        self.assertIn(b'Your todo list is empty', response.data)  # Replace with actual message

if __name__ == '__main__':
    unittest.main()