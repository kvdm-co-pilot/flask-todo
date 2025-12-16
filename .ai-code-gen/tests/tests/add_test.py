import unittest
from app import app, db, Todo
from flask import url_for, request
from contextlib import contextmanager

@contextmanager
def app_context():
    with app.app_context():
        yield

class Functional_AddValidTodoItemTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_add_valid_todo_item(self):
        data = {'title': 'Complete assignment'}
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)
        self.assertIn(b'Complete assignment', response.data)
        with app_context():
            self.assertEqual(Todo.query.count(), 1)

class Functional_FailToAddTodoWithoutTitleTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_fail_to_add_todo_without_title(self):
        data = {'title': ''}
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)
        self.assertIn(b'Title is required', response.data)

class Functional_AddTodoWithExcessivelyLongTitleTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_add_todo_with_excessively_long_title(self):
        long_title = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        data = {'title': long_title}
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)
        self.assertIn(b'Title is too long', response.data)

class Functional_AddDuplicateTodoItemTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_add_duplicate_todo_item(self):
        with app_context():
            todo = Todo(title='Buy groceries', complete=False)
            db.session.add(todo)
            db.session.commit()
        data = {'title': 'Buy groceries'}
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)
        self.assertIn(b'Item already exists', response.data)

class Functional_RenderHomepageWithEmptyTodoListTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_render_homepage_with_empty_todo_list(self):
        with app_context():
            response = self.app.get(url_for('home'))
        self.assertIn(b'To-do list is empty', response.data)

class Functional_RenderHomepageWithMultipleTodoItemsTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_render_homepage_with_multiple_todo_items(self):
        with app_context():
            todos = [
                Todo(title='Buy groceries', complete=False),
                Todo(title='Read book', complete=False),
                Todo(title='Attend meeting', complete=False)
            ]
            db.session.bulk_save_objects(todos)
            db.session.commit()
        with app_context():
            response = self.app.get(url_for('home'))
        self.assertIn(b'Buy groceries', response.data)
        self.assertIn(b'Read book', response.data)
        self.assertIn(b'Attend meeting', response.data)

class Functional_InvalidMethodForAddTodoTest(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_invalid_method_for_add_todo(self):
        with app_context():
            response = self.app.get(url_for('add'))
        self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
    unittest.main()