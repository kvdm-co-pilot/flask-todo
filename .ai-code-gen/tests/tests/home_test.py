import unittest
from app import app, db, Todo
from flask import url_for

class Functional_HomepageAccessTest(unittest.TestCase):
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

    def test_homepage_access(self):
        response = self.app.get(url_for('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Main Content', response.data)

class Functional_AddTodoValidInputTest(unittest.TestCase):
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

    def test_add_todo_valid_input(self):
        with app.app_context():
            initial_count = Todo.query.count()
        response = self.app.post(url_for('add'), data={'title': 'Buy groceries', 'status': 'Incomplete'})
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            new_count = Todo.query.count()
        self.assertEqual(new_count, initial_count + 1)

class Functional_UpdateTodoStatusTest(unittest.TestCase):
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

    def test_update_todo_status(self):
        with app.app_context():
            new_todo = Todo(title='Read book', complete=False)
            db.session.add(new_todo)
            db.session.commit()
        response = self.app.get(url_for('update', todo_id=new_todo.id))
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            updated_todo = Todo.query.get(new_todo.id)
            self.assertTrue(updated_todo.complete)

class Functional_DeleteTodoTest(unittest.TestCase):
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

    def test_delete_todo(self):
        with app.app_context():
            new_todo = Todo(title='Clean room', complete=False)
            db.session.add(new_todo)
            db.session.commit()
        response = self.app.get(url_for('delete', todo_id=new_todo.id))
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            deleted_todo = Todo.query.get(new_todo.id)
            self.assertIsNone(deleted_todo)

if __name__ == "__main__":
    unittest.main()