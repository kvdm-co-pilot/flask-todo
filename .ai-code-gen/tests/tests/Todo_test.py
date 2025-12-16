import unittest
from app import app, db, Todo
from flask import url_for
from contextlib import contextmanager

@contextmanager
def app_context():
    with app.app_context():
        yield

class TestTodoApp(unittest.TestCase):
    
    def setUp(self):
        # Given: Set up a temporary database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app_context():
            db.create_all()

    def tearDown(self):
        # Clean up database after each test
        with app_context():
            db.session.remove()
            db.drop_all()

    def test_create_todo_item_valid_title(self):
        # Given: A valid title for a new Todo
        data = {'title': 'Buy groceries'}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo should be in the database and home page
        self.assertIn(b'Buy groceries', response.data)
        self.assertEqual(Todo.query.count(), 1)

    def test_view_todo_items_display_correct_data(self):
        # Given: Multiple Todo items exist in the database
        todos = [Todo(title='Buy groceries'), Todo(title='Complete homework')]
        with app_context():
            db.session.bulk_save_objects(todos)
            db.session.commit()

        # When: The todo list page is requested
        with app_context():
            response = self.app.get(url_for('home'))

        # Then: It should display all Todo items with correct titles
        self.assertIn(b'Buy groceries', response.data)
        self.assertIn(b'Complete homework', response.data)

    def test_update_todo_item_valid_title_change(self):
        # Given: A Todo item with an existing title
        todo = Todo(title='Finish homework')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The title is updated
        with app_context():
            todo.title = 'Complete math homework'
            db.session.commit()

        # Then: The new title should be saved
        updated_todo = db.session.get(Todo, todo.id)
        self.assertEqual(updated_todo.title, 'Complete math homework')

    def test_delete_todo_item_remove_from_list(self):
        # Given: A Todo item exists in the database
        todo = Todo(title='Read book')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The delete endpoint is triggered
        with app_context():
            self.app.get(url_for('delete', todo_id=todo.id), follow_redirects=True)

        # Then: The Todo item should be removed from the database
        self.assertEqual(Todo.query.count(), 0)

    def test_create_todo_item_maximum_title_length(self):
        # Given: A title with exactly 100 characters
        data = {'title': 'A' * 100}
        
        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo should be in the database
        self.assertEqual(Todo.query.count(), 1)

    def test_create_todo_item_exceeding_title_length(self):
        # Given: A title exceeding 100 characters
        data = {'title': 'A' * 101}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data)

        # Then: An error message should be displayed
        self.assertIn(b'Title length exceeds limit', response.data)

    def test_create_todo_item_empty_title_submission(self):
        # Given: An empty title
        data = {'title': ''}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data)

        # Then: An error message should be displayed
        self.assertIn(b'Title is required', response.data)

    def test_unique_identifier_for_each_task(self):
        # Given: Multiple Todo items are created
        todos = [Todo(title='Task 1'), Todo(title='Task 2')]
        with app_context():
            db.session.bulk_save_objects(todos)
            db.session.commit()

        # Then: Each Todo item should have a unique ID
        self.assertNotEqual(todos[0].id, todos[1].id)

    def test_title_length_constraint(self):
        # Given: Titles with varying lengths
        valid_title = 'A' * 100
        invalid_title = 'A' * 101
        
        # When: Valid and invalid titles are submitted
        with app_context():
            valid_response = self.app.post(url_for('add'), data={'title': valid_title}, follow_redirects=True)
            invalid_response = self.app.post(url_for('add'), data={'title': invalid_title})

        # Then: Valid title should be accepted, invalid title rejected
        self.assertIn(b'Added successfully', valid_response.data)
        self.assertIn(b'Title length exceeds limit', invalid_response.data)

    def test_completion_status_boolean(self):
        # Given: A Todo item with a completion status
        todo = Todo(title='Study for exams', complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The status is toggled
        with app_context():
            todo.complete = True
            db.session.commit()

        # Then: The status should toggle correctly
        self.assertTrue(todo.complete)

    def test_task_completion_toggle_valid_transition(self):
        # Given: A Todo item with a 'Completed' status
        todo = Todo(title='Study for exams', complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The completion status is toggled
        with app_context():
            todo.complete = not todo.complete
            db.session.commit()

        # Then: The status should reflect the transition
        self.assertTrue(todo.complete)

    def test_task_deletion_irreversible_change(self):
        # Given: A Todo item titled 'Workout'
        todo = Todo(title='Workout')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: The item is deleted
        with app_context():
            self.app.get(url_for('delete', todo_id=todo.id), follow_redirects=True)

        # Then: It should be permanently removed
        self.assertIsNone(db.session.get(Todo, todo.id))

    def test_title_length_minimum_character(self):
        # Given: A title of 1 character
        data = {'title': 'A'}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo should be in the database
        self.assertEqual(Todo.query.count(), 1)

    def test_title_length_maximum_character(self):
        # Given: A title of 100 characters
        data = {'title': 'B' * 100}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data, follow_redirects=True)

        # Then: The new Todo should be in the database
        self.assertEqual(Todo.query.count(), 1)

    def test_title_length_empty_title(self):
        # Given: An empty title
        data = {'title': ''}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data)

        # Then: An error message should be displayed
        self.assertIn(b'Title is required', response.data)

    def test_completion_status_boolean_values(self):
        # Given: A Todo item with a completion status
        todo = Todo(title='Task', complete=True)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # Then: The completion status should accept only True or False
        self.assertIsInstance(todo.complete, bool)

    def test_completion_status_null_value(self):
        # Given: A task with completion status set to None
        todo = Todo(title='Task', complete=None)
        with app_context():
            db.session.add(todo)
        
        # When: Commit is attempted
        with self.assertRaises(ValueError):
            with app_context():
                db.session.commit()

    def test_sql_injection_attempt(self):
        # Given: A potentially malicious title
        data = {'title': "Buy groceries'; DROP TABLE Todo; --"}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data)

        # Then: The system should handle input safely
        self.assertNotIn(b'DROP TABLE', response.data)

    def test_xss_attempt(self):
        # Given: A potentially malicious title
        data = {'title': "<script>alert('XSS')</script>"}

        # When: A POST request is made to add the new Todo
        with app_context():
            response = self.app.post(url_for('add'), data=data)

        # Then: The system should sanitize input
        self.assertNotIn(b'<script>', response.data)

    def test_csrf_attack_on_update(self):
        # Given: A forged request
        todo = Todo(title='Task', complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: CSRF attack is simulated
        with app_context():
            response = self.app.post(url_for('update', todo_id=todo.id), headers={'X-CSRF-Token': 'invalid'}, follow_redirects=True)

        # Then: The system should deny the request
        self.assertIn(b'CSRF token is invalid', response.data)

    def test_id_manipulation_attack_on_update(self):
        # Given: A valid Todo item
        todo = Todo(title='Task', complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: Task ID is altered
        with app_context():
            response = self.app.post(url_for('update', todo_id=todo.id+1), follow_redirects=True)

        # Then: The system should block unauthorized updates
        self.assertIn(b'Unauthorized access', response.data)

    def test_csrf_attack_on_delete(self):
        # Given: A forged request
        todo = Todo(title='Task')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: CSRF attack is simulated
        with app_context():
            response = self.app.post(url_for('delete', todo_id=todo.id), headers={'X-CSRF-Token': 'invalid'}, follow_redirects=True)

        # Then: The system should deny the request
        self.assertIn(b'CSRF token is invalid', response.data)

    def test_id_manipulation_attack_on_delete(self):
        # Given: A valid Todo item
        todo = Todo(title='Task')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: Task ID is altered
        with app_context():
            response = self.app.post(url_for('delete', todo_id=todo.id+1), follow_redirects=True)

        # Then: The system should block unauthorized deletions
        self.assertIn(b'Unauthorized access', response.data)

    def test_database_commit_failure_on_toggle(self):
        # Given: A Todo item with a completion status
        todo = Todo(title='Task', complete=False)
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: Commit failure is simulated
        with self.assertRaises(Exception):
            with app_context():
                todo.complete = not todo.complete
                raise Exception('Commit failed')

        # Then: The system should roll back the transaction
        with app_context():
            db.session.rollback()

    def test_database_commit_failure_on_deletion(self):
        # Given: A Todo item
        todo = Todo(title='Task')
        with app_context():
            db.session.add(todo)
            db.session.commit()

        # When: Commit failure is simulated
        with self.assertRaises(Exception):
            with app_context():
                db.session.delete(todo)
                raise Exception('Commit failed')

        # Then: The system should roll back the transaction
        with app_context():
            db.session.rollback()

    def test_addition_interruptions(self):
        # Given: A title for a new Todo
        data = {'title': 'Task'}

        # When: Addition process is interrupted
        with app_context():
            response = self.app.post(url_for('add'), data=data)
            with self.assertRaises(Exception):
                raise Exception('Addition interrupted')

        # Then: No partial data should be saved
        self.assertEqual(Todo.query.count(), 0)

    def test_homepage_consistency(self):
        # Given: Multiple tasks are added
        todos = [Todo(title='Task 1'), Todo(title='Task 2')]
        with app_context():
            db.session.bulk_save_objects(todos)
            db.session.commit()

        # When: Homepage is requested
        with app_context():
            response = self.app.get(url_for('home'))

        # Then: All tasks should be displayed consistently
        self.assertIn(b'Task 1', response.data)
        self.assertIn(b'Task 2', response.data)

if __name__ == '__main__':
    unittest.main()