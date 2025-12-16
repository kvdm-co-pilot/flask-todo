import unittest
from app import app, db, Todo
from flask import url_for

class Functional_AddValidTodoItemTest(unittest.TestCase):
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

    def test_add_valid_todo_item(self):
        # Given
        with app.app_context():
            initial_count = Todo.query.count()
        title = 'Buy groceries'
        # When
        response = self.app.post(url_for('add'), data={'title': title})
        # Then
        self.assertEqual(response.status_code, 302)  # Redirection
        with app.app_context():
            new_count = Todo.query.count()
            added_todo = Todo.query.filter_by(title=title).first()
            self.assertIsNotNone(added_todo)
            self.assertFalse(added_todo.complete)
        self.assertEqual(new_count, initial_count + 1)

class Functional_AddTodoItemWithEmptyTitleTest(unittest.TestCase):
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

    def test_add_todo_item_with_empty_title(self):
        # Given
        title = ''
        # When
        response = self.app.post(url_for('add'), data={'title': title})
        # Then
        self.assertEqual(response.status_code, 400)  # Bad Request
        with app.app_context():
            added_todo = Todo.query.filter_by(title=title).first()
            self.assertIsNone(added_todo)

class Functional_AddTodoItemWithExceedingTitleLengthTest(unittest.TestCase):
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

    def test_add_todo_item_with_exceeding_title_length(self):
        # Given
        title = 'A' * 101
        # When
        response = self.app.post(url_for('add'), data={'title': title})
        # Then
        self.assertEqual(response.status_code, 400)  # Bad Request
        with app.app_context():
            added_todo = Todo.query.filter_by(title=title).first()
            self.assertIsNone(added_todo)

class Functional_ViewAllTodoItemsTest(unittest.TestCase):
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

    def test_view_all_todo_items(self):
        # Given
        with app.app_context():
            todos = [Todo(title='Item 1', complete=False), Todo(title='Item 2', complete=True)]
            db.session.bulk_save_objects(todos)
            db.session.commit()
        # When
        response = self.app.get(url_for('home'))
        # Then
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item 1', response.data)
        self.assertIn(b'Item 2', response.data)
