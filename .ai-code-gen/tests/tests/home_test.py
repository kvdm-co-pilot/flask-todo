import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from your_application import app, db, Todo  # Import the app and models

class TestTodoWebPageNavigation(unittest.TestCase):

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

    def test_add_valid_todo(self):
        # Given: A valid todo title and status
        title = 'Buy groceries'
        status = False

        # When: Adding a new todo
        response = self.app.post('/add', data={'title': title, 'status': status}, follow_redirects=True)

        # Then: Verify the todo is added successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)

    def test_update_todo_status(self):
        # Given: Add a new todo to update
        with app.app_context():
            new_todo = Todo(title='Update Status Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Updating the todo's completion status
        response = self.app.post(f'/update/{new_todo.id}', data={'complete': True}, follow_redirects=True)

        # Then: Verify the status is updated successfully
        updated_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertTrue(updated_todo.complete)

    def test_delete_existing_todo(self):
        # Given: Add a new todo to delete
        with app.app_context():
            new_todo = Todo(title='Delete Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Deleting the todo
        response = self.app.get(f'/delete/{new_todo.id}', follow_redirects=True)

        # Then: Verify the todo is deleted successfully
        deleted_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertIsNone(deleted_todo)

    def test_unique_todo_id(self):
        # Given: Add multiple todos
        titles = ['Todo 1', 'Todo 2', 'Todo 3']
        with app.app_context():
            for title in titles:
                new_todo = Todo(title=title, complete=False)
                db.session.add(new_todo)
            db.session.commit()

        # Then: Verify each todo has a unique ID
        ids = [todo.id for todo in Todo.query.all()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_title_character_limit(self):
        # Given: A todo title exceeding 100 characters
        title = 'A' * 101

        # When: Adding a new todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the system rejects the todo addition
        self.assertIn(b'Title length exceeds limit', response.data)

    def test_valid_complete_status(self):
        # Given: Add a new todo to update
        with app.app_context():
            new_todo = Todo(title='Invalid Status Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Updating the todo's completion status to a non-Boolean value
        response = self.app.post(f'/update/{new_todo.id}', data={'complete': 'complete'}, follow_redirects=True)

        # Then: Verify the system rejects the status update
        self.assertIn(b'Invalid status value', response.data)

    def test_toggle_completion_status(self):
        # Given: Add a new todo to toggle
        with app.app_context():
            new_todo = Todo(title='Toggle Status Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Toggling the todo's completion status twice
        self.app.post(f'/toggle/{new_todo.id}', follow_redirects=True)
        self.app.post(f'/toggle/{new_todo.id}', follow_redirects=True)

        # Then: Verify the status is toggled successfully
        toggled_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertFalse(toggled_todo.complete)

    def test_delete_todo_permanently(self):
        # Given: Add a new todo to delete
        with app.app_context():
            new_todo = Todo(title='Permanent Delete Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Deleting the todo and attempting retrieval
        self.app.get(f'/delete/{new_todo.id}', follow_redirects=True)
        response = self.app.get(f'/retrieve/{new_todo.id}', follow_redirects=True)

        # Then: Verify the todo is permanently deleted
        self.assertIn(b'Todo not found', response.data)

    def test_boundary_title_length_minimum(self):
        # Given: A todo title of 1 character
        title = 'A'

        # When: Adding a new todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the todo is accepted
        self.assertIn(title.encode(), response.data)

    def test_boundary_title_length_maximum(self):
        # Given: A todo title of 100 characters
        title = 'A' * 100

        # When: Adding a new todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the todo is accepted
        self.assertIn(title.encode(), response.data)

    def test_boundary_empty_title(self):
        # Given: An empty todo title
        title = ''

        # When: Adding a new todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the system rejects the todo addition
        self.assertIn(b'Title cannot be empty', response.data)

    def test_boundary_id_value_minimum(self):
        # Given: Add a todo with minimum ID value
        with app.app_context():
            new_todo = Todo(title='Minimum ID Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Performing operations on the todo
        response = self.app.get(f'/retrieve/{new_todo.id}', follow_redirects=True)

        # Then: Verify todo operations are processed correctly
        self.assertIn(new_todo.title.encode(), response.data)

    def test_boundary_id_value_max_integer(self):
        # Given: Add a todo with maximum integer ID value
        with app.app_context():
            new_todo = Todo(id=2147483647, title='Max ID Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Performing operations on the todo
        response = self.app.get(f'/retrieve/{new_todo.id}', follow_redirects=True)

        # Then: Verify system handles operations correctly
        self.assertIn(new_todo.title.encode(), response.data)

    def test_boundary_complete_status_true(self):
        # Given: Add a new todo to update
        with app.app_context():
            new_todo = Todo(title='Complete Status True Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Setting the todo's complete status to true
        response = self.app.post(f'/update/{new_todo.id}', data={'complete': True}, follow_redirects=True)

        # Then: Verify the status is updated successfully
        updated_todo = Todo.query.filter_by(id=new_todo.id).first()
        self.assertTrue(updated_todo.complete)

    def test_security_add_todo_sql_injection(self):
        # Given: A todo title with SQL injection attempt
        title = "Buy groceries'; DROP TABLE Todos;--"

        # When: Adding the todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the system prevents SQL injection
        self.assertNotIn(b'DROP TABLE', response.data)

    def test_security_add_todo_xss(self):
        # Given: A todo title with XSS attempt
        title = '<script>alert("XSS")</script>'

        # When: Adding the todo
        response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify the system sanitizes input
        self.assertNotIn(title.encode(), response.data)

    def test_security_update_todo_csrf(self):
        # Given: Forged request to update a todo's status
        with app.app_context():
            new_todo = Todo(title='CSRF Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Attempting unauthorized update
        response = self.app.post(f'/update/{new_todo.id}', data={'complete': True}, headers={'X-CSRF-Token': 'invalid'}, follow_redirects=True)

        # Then: Verify the system blocks the update
        self.assertIn(b'Unauthorized', response.data)

    def test_security_delete_todo_csrf(self):
        # Given: Forged request to delete a todo
        with app.app_context():
            new_todo = Todo(title='Delete CSRF Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Attempting unauthorized deletion
        response = self.app.get(f'/delete/{new_todo.id}', headers={'X-CSRF-Token': 'invalid'}, follow_redirects=True)

        # Then: Verify the system blocks the deletion
        self.assertIn(b'Unauthorized', response.data)

    def test_security_session_hijacking(self):
        # Given: Attempt unauthorized status change through session hijacking
        with app.app_context():
            new_todo = Todo(title='Session Hijacking Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Attempting unauthorized status change
        response = self.app.post(f'/update/{new_todo.id}', data={'complete': True}, headers={'Authorization': 'invalid'}, follow_redirects=True)

        # Then: Verify the system prevents unauthorized access
        self.assertIn(b'Unauthorized', response.data)

    def test_failure_database_transaction_failure(self):
        # Given: Simulate database transaction failure during todo addition
        title = 'Database Failure Test'

        # When: Adding a new todo with simulated DB failure
        with app.app_context():
            db.session.close()  # Simulate failure
            response = self.app.post('/add', data={'title': title, 'status': False}, follow_redirects=True)

        # Then: Verify proper error handling
        self.assertIn(b'Database error', response.data)

    def test_failure_network_issues_toggle_status(self):
        # Given: Simulate network issues during status toggle
        with app.app_context():
            new_todo = Todo(title='Network Toggle Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Simulating network failure
        # Note: Simulating network failure might be complex, consider mocking network operations
        # For simplicity, assume failure simulation
        response = self.app.post(f'/toggle/{new_todo.id}', follow_redirects=True)

        # Then: Verify recovery mechanisms
        self.assertIn(b'Network error', response.data)

    def test_failure_accidental_deletion(self):
        # Given: Test recovery options for accidental deletion
        with app.app_context():
            new_todo = Todo(title='Accidental Deletion Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Accidental deletion of the todo
        self.app.get(f'/delete/{new_todo.id}', follow_redirects=True)

        # Then: Verify support for recovery or undo
        response = self.app.get('/recover', follow_redirects=True)
        self.assertIn(b'Recovery successful', response.data)

    def test_consistency_todo_list_retrieval(self):
        # Given: Add, update, and delete todos
        with app.app_context():
            new_todo1 = Todo(title='Consistency Test 1', complete=False)
            new_todo2 = Todo(title='Consistency Test 2', complete=False)
            db.session.add(new_todo1)
            db.session.add(new_todo2)
            db.session.commit()

        # When: Performing operations on the todo list
        self.app.post(f'/update/{new_todo1.id}', data={'complete': True}, follow_redirects=True)
        self.app.get(f'/delete/{new_todo2.id}', follow_redirects=True)

        # Then: Verify UI reflects database state
        response = self.app.get('/list', follow_redirects=True)
        self.assertIn(new_todo1.title.encode(), response.data)
        self.assertNotIn(new_todo2.title.encode(), response.data)

    def test_consistency_user_interface_sync(self):
        # Given: Perform operations on the todo list
        with app.app_context():
            new_todo = Todo(title='UI Sync Test', complete=False)
            db.session.add(new_todo)
            db.session.commit()

        # When: Checking UI sync after operations
        self.app.post(f'/update/{new_todo.id}', data={'complete': True}, follow_redirects=True)

        # Then: Verify UI reflects the current state of the todo list
        response = self.app.get('/', follow_redirects=True)
        self.assertIn(b'UI Sync Test', response.data)

if __name__ == '__main__':
    unittest.main()