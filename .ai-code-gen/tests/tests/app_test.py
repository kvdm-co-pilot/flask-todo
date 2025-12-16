import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, Todo

class TodoFunctionalTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_todo_valid_title(self):
        new_title = 'Buy groceries'
        response = self.client.post('/add', data={'title': new_title}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_title.encode(), response.data)

    def test_add_todo_empty_title(self):
        response = self.client.post('/add', data={'title': ''}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title cannot be empty', response.data)

    def test_toggle_completion_status_valid_todo_id(self):
        with app.app_context():
            todo = Todo(title='Toggle Test', complete=False)
            db.session.add(todo)
            db.session.commit()
        response = self.client.get(f'/update/{todo.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        updated_todo = Todo.query.get(todo.id)
        self.assertTrue(updated_todo.complete)

    def test_toggle_completion_status_non_existent_todo_id(self):
        response = self.client.get('/update/999', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Todo item does not exist', response.data)

    def test_delete_todo_valid_todo_id(self):
        with app.app_context():
            todo = Todo(title='Delete Test', complete=False)
            db.session.add(todo)
            db.session.commit()
        response = self.client.get(f'/delete/{todo.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        deleted_todo = Todo.query.get(todo.id)
        self.assertIsNone(deleted_todo)

    def test_delete_todo_non_existent_todo_id(self):
        response = self.client.get('/delete/999', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Todo item does not exist', response.data)

    def test_title_length_limit_exceeded(self):
        long_title = 'A' * 101
        response = self.client.post('/add', data={'title': long_title}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Title cannot exceed 100 characters', response.data)

    def test_boolean_completion_status(self):
        with app.app_context():
            todo = Todo(title='Boolean Test', complete=False)
            db.session.add(todo)
            db.session.commit()
        response = self.client.get(f'/update/{todo.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        toggled_todo = Todo.query.get(todo.id)
        self.assertIsInstance(toggled_todo.complete, bool)

    def test_sql_injection_in_title(self):
        malicious_title = "'; DROP TABLE Todo; --"
        response = self.client.post('/add', data={'title': malicious_title}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid title', response.data)

    def test_xss_in_title(self):
        xss_title = '<script>alert(1)</script>'
        response = self.client.post('/add', data={'title': xss_title}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid title', response.data)

if __name__ == '__main__':
    unittest.main()