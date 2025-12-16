import unittest
from app import app, db, Todo
from flask import url_for

class TestTodoApp_AddValidTodo(unittest.TestCase):
    def setUp(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_valid_todo(self):
        # Given
        initial_count = Todo.query.count()
        
        # When
        response = self.app.post(url_for('add'), data={'title': 'Buy Groceries', 'description': 'Milk, Eggs, Bread, Butter'})
        
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertIn(url_for('home'), response.headers['Location'])
        with app.app_context():
            new_count = Todo.query.count()
            self.assertEqual(new_count, initial_count + 1)
            added_todo = Todo.query.order_by(Todo.id.desc()).first()
            self.assertEqual(added_todo.title, 'Buy Groceries')
            self.assertEqual(added_todo.description, 'Milk, Eggs, Bread, Butter')

class TestTodoApp_UpdateValidTodo(unittest.TestCase):
    def setUp(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.todo = Todo(title='Buy Groceries', description='Milk, Eggs, Bread, Butter')
            db.session.add(self.todo)
            db.session.commit()

    def tearDown(self):
        # Clean up
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_update_valid_todo(self):
        # Given
        
        # When
        response = self.app.post(url_for('update', todo_id=self.todo.id), data={'title': 'Buy Groceries', 'description': 'Milk, Eggs, Cheese'})
        
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertIn(url_for('home'), response.headers['Location'])
        with app.app_context():
            updated_todo = Todo.query.get(self.todo.id)
            self.assertEqual(updated_todo.title, 'Buy Groceries')
            self.assertEqual(updated_todo.description, 'Milk, Eggs, Cheese')

class TestTodoApp_AddTodoWithMissingTitle(unittest.TestCase):
    def setUp(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_todo_with_missing_title(self):
        # Given
        initial_count = Todo.query.count()
        
        # When
        response = self.app.post(url_for('add'), data={'title': '', 'description': 'Complete the assignment by Monday'})
        
        # Then
        self.assertEqual(response.status_code, 400)  # Bad Request
        with app.app_context():
            new_count = Todo.query.count()
            self.assertEqual(new_count, initial_count)  # No addition
            self.assertIn(b'Title is required', response.data)

class TestTodoApp_UpdateNonExistingTodo(unittest.TestCase):
    def setUp(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_update_non_existing_todo(self):
        # Given
        non_existing_id = 999
        
        # When
        response = self.app.post(url_for('update', todo_id=non_existing_id), data={'title': 'Call Mom', 'description': ''})
        
        # Then
        self.assertEqual(response.status_code, 404)  # Not Found
        self.assertIn(b'Invalid task ID', response.data)

if __name__ == "__main__":
    unittest.main()